import subprocess
from subprocess import check_output
from os.path import join
from collections import defaultdict
from islandest.misc import rename_prodigal

def execute_aragorn(infile, outfile, aragorn_path):
    bashCommand = '{aragorn} -gcbact -l -a -i -fon -o {outfile} {infile}'.format(
        aragorn=aragorn_path, outfile=outfile, infile=infile
    )
    print('aragorn command:', bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

def execute_bruce(infile, outfile, bruce_path):
    bashCommand = '{bruce} -l -o {outfile} {infile}'.format(
        bruce=bruce_path, outfile=outfile, infile=infile
    )
    print('bruce command:', bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def execute_trnascan(infile, outfile, trnascan_path, kingdom):
    bashCommand = '{trnascan} -{kingdom} -o {outfile} {infile}'.format(
        trnascan=trnascan_path, outfile=outfile, infile=infile,
        kingdom=kingdom
    )
    print('tRNAScan-SE command:', bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def execute_prodigal(infile, outgff, outfaa, outffn, prodigal_path):
    bashCommand = '{prodigal} -c -f gff -o {gff} -a {faa} -d {ffn} -i {infile}'.format(
        prodigal=prodigal_path, gff=outgff, faa=outfaa, ffn=outffn, infile=infile
    )
    print('Prodigal command:', bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    rename_prodigal(outfaa, outffn, outgff)


def execute_hmmsearch(infile, outfile, outtbl, hmmfile_path, hmmsearch_path):
    bashCommand = '{hmmsearch} -E 1 -o {out} --tblout {outtbl} {hmmfile} {seqdb}'.format(
        hmmsearch=hmmsearch_path, out=outfile, outtbl=outtbl, hmmfile=hmmfile_path, seqdb=infile
    )
    print('hmmsearch command:', bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def execute_maketdna_fasta(aragorn_tdna, bruce_tdna, trnascan_tdna, tdna_fasta_out):
    seqs = defaultdict(list)
    for tdna in aragorn_tdna:
        seqs[(tdna.contig, tdna.start, tdna.end, tdna.orient)].append(tdna)
    for tdna in bruce_tdna:
        seqs[(tdna.contig, tdna.start, tdna.end, tdna.orient)].append(tdna)
    for tdna in trnascan_tdna:
        seqs[(tdna.contig, tdna.start, tdna.end, tdna.orient)].append(tdna)

    with open(tdna_fasta_out, 'w') as outfile:
        for loc in seqs:
            print('>'+loc[0]+'::'+str(loc[1]) + '::' + str(loc[2]) + '::' + loc[3], seqs[loc][0].seq, sep='\n', file=outfile)


def execute_blast(infile, query, outfile, makeblastdb_path, blastn_path):
    bashCommand = '{makeblastdb} -parse_seqids -in {infile} -dbtype nucl'.format(
        makeblastdb=makeblastdb_path, infile=infile
    )
    print('makeblastdb command:', bashCommand)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    bashCommand = '{blastn} -query {query} -db {infile} -outfmt \'6 qaccver saccver qlen slen pident length mismatch ' \
                  'gapopen qstart qend sstart send evalue bitscore\' -out {outfile} -task blastn -gapopen 0 -gapextend ' \
                  '4 -word_size 7'.format(
        blastn=blastn_path, infile=infile, outfile=outfile, query=query
    )
    print('blast command:', bashCommand)
    bashCommand = bashCommand.split()[:6] + [' '.join(bashCommand.split()[6:21]).strip('\'')] + bashCommand.split()[21:]
    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
    output, error = process.communicate()


def execute_bedtools_intersect(a, b, bedtools_out, bedtools_path):
    bashCommand = '{bedtools} intersect -a {a} -b {b} -wa -wb > {out}'.format(
        bedtools=bedtools_path, a=a, b=b, out=bedtools_out
    )
    print('bedtools command:', bashCommand)
    proc = subprocess.Popen(bashCommand, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    with open(bedtools_out) as infile:
        for line in infile:
            line = line.strip().split()
            yield line

def execute_bedtools_getfasta(fastain, fastaout, bed, bedtools_path):
    bashCommand = '{bedtools} getfasta -fi {fi} -fo {fo} -bed {bed} -name -s'.format(
        bedtools=bedtools_path, fi=fastain, fo=fastaout, bed=bed
    )
    print('bedtools command:', bashCommand)
    proc = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()