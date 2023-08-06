import click

from subprocess import check_output
from islandest.help import CustomHelp
from islandest.run import _run

from os.path import join, dirname


ARAGORN_PATH = join(dirname(__file__), 'bin/aragorn')
BLASTN_PATH = join(dirname(__file__), 'bin/blastn')
BRUCE_PATH = join(dirname(__file__), 'bin/bruce')
HMMSEARCH_PATH = join(dirname(__file__), 'bin/hmmsearch')
HMM_PATH = join(dirname(__file__), 'data/Phage_integrase.hmm')
MAKEBLASTDB_PATH = join(dirname(__file__), 'bin/makeblastdb')
PRODIGAL_PATH = join(dirname(__file__), 'bin/prodigal')
TRNASCAN_PATH = check_output('which tRNAscan-SE'.split()).decode('utf-8').strip()
BEDTOOLS_PATH = join(dirname(__file__), 'bin/bedtools')


@click.group(cls=CustomHelp)
def cli():
    """Command-line tool to predict tDNA-targeting genomic islands"""
    pass


@cli.command(short_help='Run islandest on a complete or draft sequence of a single species.', help_priority=1)
@click.argument('fasta', type=click.Path(exists=True))
@click.option('--outdir', '-o', default='islandest_output')
@click.option('--aragorn-path', default=ARAGORN_PATH, type=click.Path(exists=True))
@click.option('--blastn-path', default=BLASTN_PATH, type=click.Path(exists=True))
@click.option('--bruce-path', default=BRUCE_PATH, type=click.Path(exists=True))
@click.option('--hmmsearch-path', default=HMMSEARCH_PATH, type=click.Path(exists=True))
@click.option('--hmm-path', default=HMM_PATH, type=click.Path(exists=True))
@click.option('--makeblastdb-path', default=MAKEBLASTDB_PATH, type=click.Path(exists=True))
@click.option('--prodigal-path', default=PRODIGAL_PATH, type=click.Path(exists=True))
@click.option('--trnascan-path', default=TRNASCAN_PATH, type=click.Path(exists=True))
@click.option('--bedtools-path', default=BEDTOOLS_PATH, type=click.Path(exists=True))
@click.option('--force/--no-force', default=False, help="Force overwriting of output directory.")
@click.option('--keep-going/--no-keep-going', default=False, help="Overwrite outputs if already exist.")
def run(fasta, outdir, aragorn_path, blastn_path, bruce_path, hmmsearch_path, hmm_path, makeblastdb_path, prodigal_path,
        trnascan_path, bedtools_path, force, keep_going):
    """A click access point for the run module. This is used for creating the command line interface."""
    log_params(command='run', fasta=fasta, outdir=outdir, aragorn_path=aragorn_path, blastn_path=blastn_path,
               bruce_path=bruce_path, hmmsearch_path=hmmsearch_path, hmm_path=hmm_path, makeblastdb_path=makeblastdb_path,
               prodigal_path=prodigal_path, trnascan_path=trnascan_path, bedtools_path=bedtools_path,
               force=force, keep_going=keep_going)

    _run(fasta, outdir, aragorn_path, blastn_path, bruce_path, hmmsearch_path, hmm_path, makeblastdb_path,
         prodigal_path, trnascan_path, bedtools_path, force, keep_going)


def log_params(**kwargs):
    click.echo("#### PARAMETERS ####")
    click.echo('\n'.join(list(map(lambda x: ': '.join(list(map(str, x))), kwargs.items()))))
    click.echo("####################")


if __name__ == '__main__':

    cli()
