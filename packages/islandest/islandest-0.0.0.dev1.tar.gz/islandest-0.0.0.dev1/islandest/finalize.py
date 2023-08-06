import sys
from os.path import join
from islandest.execute import execute_bedtools_getfasta

def _finalize(blast_hits, aragorn_tdna, bruce_tdna, trnascan_tdna, fasta, outdir, bedtools_path):

    outbedfile = join(outdir, 'islandest_results.bed')
    make_bed_file(blast_hits, aragorn_tdna, bruce_tdna, trnascan_tdna, outbedfile)
    outfastafile = join(outdir, 'islandest_results.fna')
    execute_bedtools_getfasta(fasta, outfastafile, outbedfile, bedtools_path)


def make_bed_file(blast_hits, aragorn_tdna, bruce_tdna, trnascan_tdna, outbedfile):

    with open(outbedfile, 'w') as outfile:
        print('#gffTags', file=outfile)
        print('track name="IslandestResults" description="Island regions identified by ISLANDEST" itemRgb="On"', file=outfile)
        out = []
        tdna_count = 0
        protein_count = 0
        for i, key in enumerate(blast_hits):
            contig, start, end, orient = key.split('::')
            start, end = int(start), int(end)

            if orient == 'F':
                orient = '+'
            else:
                orient = '-'

            aragorn, bruce, trnascan = get_tdna(contig, start, end, aragorn_tdna, bruce_tdna, trnascan_tdna)
            tdna_details = ''
            if aragorn is not None:
                tdna_details += 'aragorn_tDNA_type=' + aragorn.type + ';aragorn_amino_acid=' + aragorn.amino_acid + ';aragorn_codon=' + aragorn.codon + ';'
            if bruce is not None:
                tdna_details += 'bruce_tDNA_type=' + bruce.type + ';bruce_amino_acid=' + bruce.amino_acid + ';bruce_codon=' + bruce.codon + ';'
            if trnascan is not None:
                tdna_details += 'trnascan_tDNA_type=' + trnascan.type + ';trnascan_amino_acid=' + trnascan.amino_acid + ';trnascan_codon=' + trnascan.codon + ';'

            out.append([contig, start, end, 'ID=tDNA'+str(i+1) + ';' + tdna_details, 0, orient, int(start), int(end), '255,0,0'])

            for res in blast_hits[key]:

                tdna_count += 1

                res_orient = '-'
                if res['hit_orient'] == 'F':
                    res_orient = '+'

                tDNA_end = res['tdna_end']
                out.append([res['saccver'], int(res['island_start']), int(res['island_end']), 'ID=Island' + str(tdna_count) + ';Parent=' + 'tDNA'+str(i+1) + ';tDNA_end=' + tDNA_end + ';', 0, res_orient, int(res['island_start']), int(res['island_end']), '0,0,255'])
                out.append([res['saccver'], int(res['sstart']), int(res['send']), 'ID=Frag' + str(tdna_count) + ';Parent=' + 'Island' + str(tdna_count) + ';tDNA_end=' + tDNA_end + ';', 0, res_orient, int(res['sstart']), int(res['send']), '0,255,0'])

                for integ, integ_contig, integ_start, integ_end, orient in res['integrases']:
                    protein_count += 1
                    out.append([integ_contig, integ_start, integ_end, 'ID=Integrase' + str(protein_count)+ ';Parent=' + 'Island' + str(tdna_count) + ';tDNA_end=' + tDNA_end + ';', 0, orient, integ_start, integ_end, '0,255,255'])

        out = sorted(out, key = lambda x: (x[0], x[1], x[2]))
        for res in out:
            print(*res, sep='\t', file=outfile)


def get_tdna(contig, start, end, aragorn, bruce, trnascan):
    out_aragorn = None
    out_bruce = None
    out_trnascan = None


    for tdna in aragorn:
        if tdna.contig == contig and tdna.start == start and tdna.end == end:
            out_aragorn = tdna
            break

    for tdna in bruce:
        if tdna.contig == contig and tdna.start == start and tdna.end == end:
            out_bruce = tdna
            break

    for tdna in trnascan:
        if tdna.contig == contig and tdna.start == start and tdna.end == end:
            out_trnascan = tdna
            break

    return out_aragorn, out_bruce, out_trnascan


