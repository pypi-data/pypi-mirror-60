import math
import os
import shutil

from subsample_fastas import subsample_fastas

EXAMPLE_DIR = "tests/data/"
EXAMPLE_FILE = "tests/data/example1.fasta"
OUTPUT_DIR = "tests/data/output"


def test_fasta_alteration_single_file():
    """test the package with a single file as input
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    pc_removed, fasta_path = subsample_fastas.alter_fasta_file(
        EXAMPLE_FILE, 0.05, os.path.join(OUTPUT_DIR, "test.fasta")
    )
    assert math.isclose(pc_removed, (1 - 281 / 296) * 100, abs_tol=0.00001)
    # clean
    shutil.rmtree(OUTPUT_DIR)


def test_main():
    # main([])
    test_fasta_alteration_single_file
