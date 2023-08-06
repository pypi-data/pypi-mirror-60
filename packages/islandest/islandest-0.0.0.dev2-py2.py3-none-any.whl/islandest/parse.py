from Bio import SeqIO
import re
from islandest.misc import revcomp
from islandest.execute import execute_bedtools_intersect
from collections import defaultdict
import sys

class tDNA:

    contig = None
    start = None
    end = None
    seq = None
    orient = None
    type = None
    amino_acid = None
    codon = None

    def __init__(self, contig, start, end, seq, orient, type, amino_acid, codon):
        self.contig = contig
        self.start = start
        self.end = end
        self.seq = seq
        self.orient = orient
        self.type = type
        self.amino_acid = amino_acid
        self.codon = codon

    def __str__(self):
        out = ''
        out += 'contig: {0}\n'.format(self.contig)
        out += 'start: {0}\n'.format(self.start)
        out += 'end: {0}\n'.format(self.end)
        out += 'seq: {0}\n'.format(self.seq)
        out += 'orient: {0}\n'.format(self.orient)
        out += 'type: {0}\n'.format(self.type)
        out += 'amino_acid: {0}\n'.format(self.amino_acid)
        out += 'codon: {0}\n'.format(self.codon)

        return out

    def __hash__(self):
        return hash((self.contig, self.start, self.end, self.seq, self.orient,
                     self.type, self.amino_acid, self.codon))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __lt__(self, other):

        if self.contig != other.contig:
            return self.contig < other.contig

        return self.start < other.start

class AragornParser:

    filein = None
    input_fasta = None
    input_fasta_recids = None
    tDNAs = None

    def __init__(self, aragorn_out, input_fasta):

        self.filein = aragorn_out
        self.input_fasta = input_fasta
        self.parse_input_fasta()
        self.parse()

    def parse_input_fasta(self):
        tmp = {}
        self.input_fasta_recids = [None]
        for rec in SeqIO.parse(self.input_fasta, 'fasta'):
            tmp[rec.id] = str(rec.seq).upper()
            self.input_fasta_recids.append(rec.id)
        self.input_fasta = tmp

    def parse(self):

        self.tDNAs = set()

        for rec in SeqIO.parse(self.filein, 'fasta'):
            contig = self.input_fasta_recids[int(rec.id.split('-')[0])]
            start, end = list(map(int, rec.description.split('[')[-1].strip(']').split(',')))
            start -= 1
            tdna_type = rec.description.split()[1].split('-')[0]
            if tdna_type == 'tRNA':
                amino_acid = rec.description.split()[1].split('-')[1].split('(')[0]
                codon = rec.description.split()[1].split('-')[1].split('(')[-1].strip(')').upper()
            else:
                amino_acid = None
                codon = None

            if tdna_type == 'tRNA' and len(rec.seq) > 150:
                continue

            if 'c[' in rec.description:
                orient = 'R'
            else:
                orient = 'F'

            tdna = tDNA(contig, start, end, str(rec.seq.upper()), orient, tdna_type, amino_acid, codon)

            self.tDNAs.add(tdna)


class BruceParser:

    filein = None
    input_fasta = None
    input_fasta_recids = None
    tDNAs = None

    def __init__(self, bruce_out, input_fasta):

        self.filein = bruce_out
        self.input_fasta = input_fasta
        self.parse_input_fasta()
        self.parse()

    def parse_input_fasta(self):
        tmp = {}
        self.input_fasta_recids = [None]
        for rec in SeqIO.parse(self.input_fasta, 'fasta'):
            tmp[rec.id] = str(rec.seq).upper()
            self.input_fasta_recids.append(rec.id)
        self.input_fasta = tmp

    def parse(self):

        self.tDNAs = set()

        new_finding_lines = []
        with open(self.filein) as infile:
            for i, line in enumerate(infile):
                matches = re.findall(r'^\d+\.', line)
                if len(matches) > 0:
                    new_finding_lines.append(i)

        findings = []
        with open(self.filein) as infile:
            keep = False
            finding = []
            for i, line in enumerate(infile):
                line = line.strip()
                if i in new_finding_lines:
                    keep=True
                    if len(finding) > 0:
                        findings.append(finding)
                    findings = []
                if keep:
                    finding.append(line)

            findings.append(finding)

        for find in findings:
            if len(find) == 0:
                continue

            contig = [line for line in find if ' Sequence in ' in line][0].split()[3]

            coord = [line for line in find if line.startswith('Sequence') and line.endswith(']')][0].split()[-1]
            start, end = list(map(int, coord.split('[')[-1].strip(']').split(',')))
            start -= 1
            orient = 'F'
            if coord.startswith('c'):
                orient = 'R'

            seq = self.input_fasta[contig][start:end]
            if orient == 'R':
                seq = revcomp(seq)

            tdna = tDNA(contig, start, end, seq, orient, 'tmRNA', None, None)
            self.tDNAs.add(tdna)


class tRNAscanParser:

    filein = None
    input_fasta = None
    input_fasta_recids = None
    tDNAs = None

    def __init__(self, trnascan_out, input_fasta):

        self.filein = trnascan_out
        self.input_fasta = input_fasta
        self.parse_input_fasta()
        self.parse()

    def parse_input_fasta(self):
        tmp = {}
        self.input_fasta_recids = [None]
        for rec in SeqIO.parse(self.input_fasta, 'fasta'):
            tmp[rec.id] = str(rec.seq).upper()
            self.input_fasta_recids.append(rec.id)
        self.input_fasta = tmp

    def parse(self):

        self.tDNAs = set()
        header = ['contig', 'num', 'start', 'end', 'amino_acid', 'codon',
                  'intron_start', 'intron_end', 'score', 'note']
        with open(self.filein) as infile:
            infile.readline(), infile.readline(), infile.readline()
            for line in infile:
                line = line.strip().split()
                line = {header[i]:line[i] for i in range(len(line))}
                if line['amino_acid'] == 'Undet':
                    continue
                if 'note' in line and 'pseudo' in line['note']:
                    continue
                contig, start, end = line['contig'], int(line['start']), int(line['end'])

                orient = 'F'
                if end < start:
                    orient = 'R'
                    tmp = start
                    start = end
                    end = tmp
                start -= 1

                seq = self.input_fasta[contig][start:end].upper()
                if orient == 'R':
                    seq = revcomp(seq)

                tdna = tDNA(contig, start, end, seq, orient, 'tRNA', line['amino_acid'], line['codon'].upper())
                self.tDNAs.add(tdna)


class BlastParser:

    blastfile = None
    hits = None

    def __init__(self, blastfile):
        self.blastfile = blastfile
        self.parse()

    def parse(self):
        self.hits = defaultdict(list)
        header = ['qaccver', 'saccver', 'qlen', 'slen', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend',
                  'sstart', 'send', 'evalue', 'bitscore']
        with open(self.blastfile) as infile:
            for line in infile:
                line = line.strip().split()
                line = {header[i]:line[i] for i in range(len(line))}
                hit_orient = 'F'
                if line['sstart'] > line['send']:
                    hit_orient = 'R'
                    tmp = line['sstart']
                    line['sstart'] = line['send']
                    line['send'] = tmp

                line['hit_orient'] = hit_orient

                for key in line:
                    try:
                        line[key] = float(line[key])
                    except ValueError:
                        continue

                line['sstart'] -= 1
                line['qstart'] -= 1

                self.hits[line['qaccver']].append(line)

    def filter_hits_complete_tdna(self, tdna_fasta):
        filtered = defaultdict(list)

        complete_trna_coords = []
        for rec in SeqIO.parse(tdna_fasta, 'fasta'):
            contig, start, end, orient = rec.id.split('::')
            start, end = int(start), int(end)
            complete_trna_coords.append((contig, start, end))

        for key in self.hits:
            for hit in self.hits[key]:
                overlaps_tdna = False
                for coord in complete_trna_coords:
                    if coord[0] != hit['saccver']:
                        continue
                    if coord[1] <= hit['send'] and coord[2] >= hit['sstart']:
                        overlaps_tdna = True
                        break
                if not overlaps_tdna:
                    filtered[key].append(hit)

        self.hits = filtered

    def filter_hits_different_contig(self):
        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:
                query_contig = hit['qaccver'].split('::')[0]
                hit_contig = hit['saccver']

                if query_contig == hit_contig:
                    filtered[key].append(hit)

        self.hits = filtered

    def filter_internal_fragment(self):
        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:
                qlen = hit['qlen']
                qstart = hit['qstart']
                qend = hit['qend']

                if qlen == qend or qstart == 0:
                    filtered[key].append(hit)

        self.hits = filtered


    def filter_configuration(self):

        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:
                tdna_contig, tdna_start, tdna_end, tdna_orient = hit['qaccver'].split('::')
                tdna_start, tdna_end = int(tdna_start), int(tdna_end)
                sstart, send = hit['sstart'], hit['send']
                qlen, qstart, qend = hit['qlen'], hit['qstart'], hit['qend']
                alen = hit['length']

                if qstart == 0:
                    end = '5p'
                elif qend == qlen:
                    end = '3p'

                hit['tdna_end'] = end
                hit['tdna_orient'] = tdna_orient

                if tdna_orient == 'F' and end == '5p' and sstart < tdna_start:
                    island_start, island_end = send, tdna_start + alen
                    hit['island_start'] = island_start
                    hit['island_end'] = island_end
                    filtered[key].append(hit)
                elif tdna_orient == 'F' and end == '3p' and sstart > tdna_end:
                    island_start, island_end = tdna_end - alen, sstart
                    hit['island_start'] = island_start
                    hit['island_end'] = island_end
                    filtered[key].append(hit)
                elif tdna_orient == 'R' and end == '5p' and sstart > tdna_end:
                    island_start, island_end = tdna_end - alen, sstart
                    hit['island_start'] = island_start
                    hit['island_end'] = island_end
                    filtered[key].append(hit)
                elif tdna_orient == 'R' and end == '3p' and sstart < tdna_start:
                    island_start, island_end = send, tdna_start + alen
                    hit['island_start'] = island_start
                    hit['island_end'] = island_end
                    filtered[key].append(hit)

        self.hits = filtered

    def filter_orientation(self):
        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:
                if hit['tdna_orient'] == hit['hit_orient']:
                    filtered[key].append(hit)

        self.hits = filtered


    def filter_cds_overlap(self, outfile, bedtools_out, hmmsearch_tbl, prodigal_gff, bedtools_path):
        integrase_cds = set()
        with open(hmmsearch_tbl) as infile:
            for line in infile:
                if line.startswith('#'):
                    continue
                integrase_cds.add(line.strip().split()[0])

        with open(outfile, 'w') as out:
            for key in self.hits:
                for hit in self.hits[key]:
                    print(hit['saccver'], int(hit['sstart']), int(hit['send']), key, sep='\t', file=out)

        exclude = set()
        for line in execute_bedtools_intersect(outfile, prodigal_gff, bedtools_out, bedtools_path):
            cds = line[-1][3:].split(';')[0]
            if cds not in integrase_cds:
                exclude.add(tuple(line[:4]))

        filtered = defaultdict(list)
        for key in self.hits:
            for hit in self.hits[key]:
                check = tuple([hit['saccver'], str(int(hit['sstart'])), str(int(hit['send'])), key])
                if check not in exclude:
                    filtered[key].append(hit)
        self.hits = filtered


    def mark_tandems(self):
        filtered = defaultdict(list)
        for key in self.hits:
            if len(self.hits[key]) > 1:

                hits = self.hits[key]
                hits_5p = [hit for hit in hits if hit['tdna_end'] == '5p']
                hits_3p = [hit for hit in hits if hit['tdna_end'] == '3p']

                if len(hits_3p) > 0 and hits_3p[0]['tdna_orient'] == 'F':
                    hits = sorted(hits_3p, key=lambda x: x['sstart'])
                    prev_sstart = None
                    prev_alen = None
                    for hit in hits:
                        hit['tandem'] = True
                        if prev_sstart is None:
                            prev_sstart = hit['sstart']
                            prev_alen = hit['length']
                        else:
                            hit['island_start'] = prev_sstart + max([0, (prev_alen - hit['length'])])
                            prev_sstart = hit['sstart']
                            prev_alen = hit['length']

                        filtered[key].append(hit)

                if len(hits_3p) > 0 and hits_3p[0]['tdna_orient'] == 'R':
                    hits = list(reversed(sorted(hits_3p, key=lambda x: x['send'])))
                    prev_send = None
                    prev_alen = None
                    for hit in hits:
                        hit['tandem'] = True
                        if prev_send is None:
                            prev_send = hit['send']
                            prev_alen = hit['length']
                        else:
                            hit['island_end'] = prev_send - max([0, (prev_alen - hit['length'])])
                            prev_send = hit['send']
                            prev_alen = hit['length']

                        filtered[key].append(hit)

                if len(hits_5p) > 0 and hits_5p[0]['tdna_orient'] == 'F':
                    hits = list(reversed(sorted(hits_5p, key=lambda x: x['send'])))
                    prev_send = None
                    prev_alen = None
                    for hit in hits:
                        hit['tandem'] = True
                        if prev_send is None:
                            prev_send = hit['send']
                            prev_alen = hit['length']
                        else:
                            hit['island_end'] = prev_send - max([0, (prev_alen - hit['length'])])
                            prev_send = hit['send']
                            prev_alen = hit['length']

                        filtered[key].append(hit)

                if len(hits_5p) > 0 and hits_5p[0]['tdna_orient'] == 'R':
                    hits = sorted(hits_5p, key=lambda x: x['sstart'])
                    prev_sstart = None
                    prev_alen = None
                    for hit in hits:
                        hit['tandem'] = True
                        if prev_sstart is None:
                            prev_sstart = hit['sstart']
                            prev_alen = hit['length']
                        else:
                            hit['island_start'] = prev_sstart + max([0, (prev_alen - hit['length'])])
                            prev_sstart = hit['sstart']
                            prev_alen = hit['length']

                        filtered[key].append(hit)

            else:
                for hit in self.hits[key]:
                    filtered[key].append(hit)

        self.hits = filtered

    def filter_island_size(self):
        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:
                island_start, island_end = hit['island_start'], hit['island_end']

                island_length = island_end - island_start
                if island_length > 2000 and island_length < 200000:
                    filtered[key].append(hit)

        self.hits = filtered

    def filter_integrase(self, hmmsearch_tbl, prodigal_out_gff):
        integrase_cds = set()
        with open(hmmsearch_tbl) as infile:
            for line in infile:
                if line.startswith('#'):
                    continue
                integrase_cds.add(line.strip().split()[0])

        cds_coords = []
        with open(prodigal_out_gff) as infile:
            for line in infile:
                line = line.strip().split()
                cds = line[-1][3:].split(';')[0]
                if cds in integrase_cds:
                    cds_coords.append([cds, line[0], int(line[3])-1, int(line[4]), line[6]])

        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:
                overlapping_integrase = []
                for cds, contig, start, end, orient in cds_coords:
                    if contig != hit['saccver']:
                        continue
                    if start <= hit['island_end'] and end >= hit['island_start']:
                        overlapping_integrase.append([cds, contig, start, end, orient])
                if len(overlapping_integrase) > 0:
                    hit['integrases'] = overlapping_integrase
                    filtered[key].append(hit)
        self.hits = filtered

    def filter_integrase_edgedistance(self, edgedist=10000):

        filtered = defaultdict(list)

        for key in self.hits:
            for hit in self.hits[key]:

                for cds, contig, start, end, orient in hit['integrases']:
                    mindist = min([abs(hit['island_start'] - start), abs(hit['island_end']-start),
                                   abs(hit['island_start'] - end), abs(hit['island_end']-end)])
                    if mindist <= edgedist:
                        filtered[key].append(hit)
                        break

        self.hits = filtered