from Bio import SeqIO
from random import choices
import string

def revcomp(seq):
    out = ''
    revdict = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}
    for c in seq[::-1]:
        try:
            out += revdict[c]
        except KeyError:
            out += c
    return out

def parse_gff(gff):
    with open(gff) as infile:
        for line in infile:
            if not line.startswith('#') and len(line) > 10:
                yield line.strip()

def rename_prodigal(faa, ffn, gff):
    out_faa, out_ffn, out_gff = [], [], []
    prefix = ''.join(list(choices(string.ascii_uppercase, k=6)))
    num = 0
    for faa_rec, ffn_rec, gff_rec in zip(SeqIO.parse(faa, 'fasta'), SeqIO.parse(ffn, 'fasta'), parse_gff(gff)):
        num += 1
        new_id = prefix+'_'+str(num)

        faa_rec.id = new_id
        faa_rec.name = new_id
        desc = faa_rec.description.split()
        desc[-1] = 'ID='+new_id+';'+';'.join(desc[-1].split(';')[1:])
        faa_rec.description = ' '.join(desc)
        out_faa.append(faa_rec)

        ffn_rec.id = new_id
        ffn_rec.name = new_id
        desc = ffn_rec.description.split()
        desc[-1] = 'ID=' + new_id + ';' + ';'.join(desc[-1].split(';')[1:])
        ffn_rec.description = ' '.join(desc)
        out_ffn.append(ffn_rec)

        gff_rec = gff_rec.split('\t')
        gff_rec[-1] = 'ID=' + new_id + ';' + ';'.join(gff_rec[-1].split(';')[1:])
        out_gff.append('\t'.join(gff_rec))

    SeqIO.write(out_faa, faa, 'fasta')
    SeqIO.write(out_ffn, ffn, 'fasta')
    with open(gff, 'w') as outfile:
        print(*out_gff, sep='\n', file=outfile)