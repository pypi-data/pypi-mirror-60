"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -msubsample_fastas` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``subsample_fastas.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``subsample_fastas.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import logging
import os
import sys

from subsample_fastas.utils import is_valid_dir

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Command description.")
parser.add_argument(
    "--fasta",
    "-f",
    metavar="FASTA",
    required=True,
    nargs="+",
    help="A fasta file, a list of fasta files or a directory with fasta files to be altered",
)
parser.add_argument(
    "--outputdir", "-o", metavar="FASTA", required=True, help="Output directory"
)
parser.add_argument(
    "--force",
    required=False,
    action="store_true",
    help="Overwrite files in output directory if they already exist",
)
parser.add_argument(
    "-pg",
    metavar="PERCENT OF GENES",
    type=float,
    default=5,
    help="Percentage of genes to be removed",
)
parser.add_argument(
    "-pf",
    metavar="PERCENT OF FILES",
    type=float,
    default=100,
    help="Percentage of files to be altered",
)


def main(args=None):
    args = parser.parse_args(args=args)
    # analyse the main input: fasta file(s) or directory
    input_dir = None
    input_file = None
    input_list = None
    if len(args.fasta) == 1:
        # either a single file or a dir
        if os.path.isfile(args.fasta[0]):
            input_file = args.fasta[0]
        elif os.path.isdir(args.fasta[0]):
            input_dir = args.fasta[0]
        else:
            logger.critical("Input is incorrect")
            sys.exit(1)
    else:
        # has to be a list of fasta files
        if all(os.path.isfile(i) for i in args.fasta):
            input_list = args.fasta

    if not is_valid_dir(args.outputdir):
        logger.critical("Impossible to access/create output directory")
        sys.exit(1)

    return (
        input_dir,
        input_file,
        input_list,
        args.pg,
        args.pf,
        args.outputdir,
        args.force,
    )
