"""
Entrypoint module, in case you use `python -msubsample_fastas`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

# flake8: noqa E501

import logging
import sys
from os import listdir
from os.path import basename
from os.path import isfile
from os.path import join

from subsample_fastas.cli import main
from subsample_fastas.subsample_fastas import alter_fasta_file
from subsample_fastas.subsample_fastas import select

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    fasta_dir, fasta_file, fasta_list, pc_genes, pc_files, outdir, forceoption = main()
    if fasta_dir:
        input_f = [
            join(fasta_dir, f) for f in listdir(fasta_dir) if isfile(join(fasta_dir, f))
        ]
    elif fasta_file:
        input_f = [fasta_file]
    else:
        input_f = fasta_list

    if pc_files != 100:
        if len(input_f) > 1:
            size_before = len(input_f)
            input_f = select(input_f, pc_files / 100)
            logger.info(
                f"Treatment will be done on {len(input_f)} files out of {size_before} (desired ratio = {pc_files}% ; actual ratio = {len(input_f)/size_before*100:.2f}%)"
            )
        else:
            logger.warning(
                f"A single file was provided. The percentage of files to be altered cannot be != 100. Assuming pf = 100%."
            )

    for fasta_file in input_f:
        filename = basename(fasta_file)
        if (not isfile(join(outdir, filename))) or forceoption:
            pc_keptgenes, outfile = alter_fasta_file(
                fasta_file, pc_genes / 100, join(outdir, filename)
            )
            logger.info(f"{pc_keptgenes:.2f}% removed genes in {outfile}.")
        else:
            logger.critical(
                f"{join(outdir,filename)} already exists. Consider using the --force option to overwrite existing files"
            )
            sys.exit(1)
