from enum import Enum

from pydantic import BaseModel

from .rc import RC, StrRC

__all__ = ["ErrorResponse", "FastaType"]


class ErrorResponse(BaseModel):
    rc: StrRC = StrRC.EFAIL
    msg: str = "something went wrong"

    @classmethod
    def create(cls, rc: RC, msg: str):
        return cls(rc=StrRC[rc.name], msg=msg)


class FastaType(str, Enum):
    state = "state"
    frag = "frag"
    codon = "codon"
    amino = "amino"
