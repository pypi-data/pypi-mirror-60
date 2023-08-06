import sys
from os.path import join, isdir, isfile
from os import makedirs
from islandest.execute import *
from islandest.parse import *
from islandest.finalize import _finalize
from shutil import rmtree, copyfile

def _run(fasta, outdir, aragorn_path, blastn_path, bruce_path, hmmsearch_path, hmm_path, makeblastdb_path, prodigal_path,
         trnascan_path, bedtools_path, force, keep_going, kingdom):

    if force:
        print("Removing output directory if it exists...")
        if isdir(outdir):
            rmtree(outdir)

    tmpdir = join(outdir, 'tmp')
    tmpfasta = join(tmpdir, 'input.fna')

    try:
        makedirs(outdir)
        makedirs(tmpdir)
    except FileExistsError:
        if not keep_going:
            print("Output directory already exists, override using the --force or --keep-going option.")
            sys.exit()

    if not isfile(tmpfasta):
        copyfile(fasta, tmpfasta)

    aragorn_out = join(tmpdir, 'Aragorn.out')
    if not isfile(aragorn_out):
        execute_aragorn(tmpfasta, aragorn_out, aragorn_path)
    else:
        print("Aragorn already complete, continuing...")

    bruce_out = join(tmpdir, 'Bruce.out')
    if not isfile(bruce_out):
        execute_bruce(tmpfasta, bruce_out, bruce_path)
    else:
        print("Bruce already complete, continuing...")

    trnascan_out = join(tmpdir, 'tRNAscan.out')
    if not isfile(trnascan_out):
        execute_trnascan(tmpfasta, trnascan_out, trnascan_path, kingdom)
    else:
        print("tRNAscan already complete, continuing...")

    aragorn_tdna = AragornParser(aragorn_out, tmpfasta).tDNAs
    print("Total tDNAs found by Aragorn: {0}".format(len(aragorn_tdna)))

    bruce_tdna = BruceParser(bruce_out, tmpfasta).tDNAs
    print("Total tDNAs found by Bruce: {0}".format(len(bruce_tdna)))

    trnascan_tdna = tRNAscanParser(trnascan_out, tmpfasta).tDNAs
    print("Total tDNAs found by tRNAscan: {0}".format(len(trnascan_tdna)))

    prodigal_out_gff = join(tmpdir, 'prodigal.gff')
    prodigal_out_faa = join(tmpdir, 'prodigal.faa')
    prodigal_out_ffn = join(tmpdir, 'prodigal.ffn')
    if not isfile(prodigal_out_gff) or not isfile(prodigal_out_faa) or not isfile(prodigal_out_ffn):
        execute_prodigal(tmpfasta, prodigal_out_gff, prodigal_out_faa, prodigal_out_ffn, prodigal_path)
    else:
        print("Prodigal already complete, continuing...")

    hmmsearch_out = join(tmpdir, 'hmmsearch.out')
    hmmsearch_tbl = join(tmpdir, 'hmmsearch.tbl')
    if not isfile(hmmsearch_out) or not isfile(hmmsearch_tbl):
        execute_hmmsearch(prodigal_out_faa, hmmsearch_out, hmmsearch_tbl, hmm_path, hmmsearch_path)
    else:
        print("HMMSEARCH already complete, continuing...")

    tdna_fasta_out = join(tmpdir, 'tdna.fna')
    if not isfile(tdna_fasta_out):
        execute_maketdna_fasta(aragorn_tdna, bruce_tdna, trnascan_tdna, tdna_fasta_out)

    blast_out = join(tmpdir, 'tdna.input.blast.tsv')
    if not isfile(blast_out):
        execute_blast(tmpfasta, tdna_fasta_out, blast_out, makeblastdb_path, blastn_path)
    else:
        print("BLASTN already complete, continuing...")

    print("Parsing BLASTN results...")
    blast_results = BlastParser(blast_out)
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits to separate contigs...")
    blast_results.filter_hits_different_contig()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by internal fragments...")
    blast_results.filter_internal_fragment()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits to full tDNAs...")
    blast_results.filter_hits_complete_tdna(tdna_fasta_out)
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by configuration...")
    blast_results.filter_configuration()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by orientation...")
    tmpout = join(tmpdir, 'hits.tmp')
    bedtools_out = join(tmpdir, 'bedtools.out')
    blast_results.filter_cds_overlap(tmpout, bedtools_out, hmmsearch_tbl, prodigal_out_gff, bedtools_path)
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by CDS overlap...")
    blast_results.filter_orientation()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Marking tandem islands...")
    blast_results.mark_tandems()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by island size...")
    blast_results.filter_island_size()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by integrase CDS...")
    blast_results.filter_integrase(hmmsearch_tbl, prodigal_out_gff)
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))
    print("Filtering out hits by integrase CDS to edge distance...")
    blast_results.filter_integrase_edgedistance()
    print(sum([1 for key in blast_results.hits for i in blast_results.hits[key]]))

    _finalize(blast_results.hits, aragorn_tdna, bruce_tdna, trnascan_tdna, tmpfasta, outdir, bedtools_path)

