from enum import Enum

__all__ = ["FastaType"]


class FastaType(str, Enum):
    state = "state"
    frag = "frag"
    codon = "codon"
    amino = "amino"
