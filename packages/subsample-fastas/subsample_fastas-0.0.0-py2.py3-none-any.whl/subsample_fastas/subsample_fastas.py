import logging
import sys
from random import sample

from Bio import SeqIO

logger = logging.getLogger(__name__)


def select(l, n):
    """select a percentage of items in a list
    
    Args:
        l (list): list of items
        n (float): percentage of items to be kept
    
    Returns:
        list: list of selected items
    """
    return sample(l, int(len(l) * n + 0.5))


def alter_fasta_file(in_fasta, n, out_fasta):
    """alter the fasta file by removing a percentage of genes
    
    Args:
        in_fasta (str): path to a fasta file
        n (float): percentage of genes to be removed
        out_fasta (str): path to a fasta file
    """
    with open(in_fasta) as f:
        # count the genes without Biopython (faster?)
        # nb_before = len([1 for line in f.readlines() if line.startswith(">")])
        seqs = SeqIO.parse(f, "fasta")
        list_seq = list(seqs)
        nb_before = len(list_seq)
        if nb_before == 0:
            logger.critical(
                f"Could not read {in_fasta} with BioPython. Please check the file or remove it from the input data"
            )
            sys.exit(1)
        nb_kept = nb_before - int(n * nb_before + 0.5)
        nb_removed = nb_before - nb_kept
        # print(nb_before, nb_removed, nb_kept, n)
        pc_removed_genes = nb_removed / nb_before * 100
        # genes to be kept
        kept_genes = sample(list_seq, nb_kept)
        SeqIO.write(kept_genes, out_fasta, "fasta")
    return pc_removed_genes, out_fasta
