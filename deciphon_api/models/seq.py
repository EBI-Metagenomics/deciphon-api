from __future__ import annotations

from typing import List, Optional

from deciphon_sched.seq import (
    sched_seq,
    sched_seq_get_all,
    sched_seq_get_by_id,
    sched_seq_new,
    sched_seq_scan_next,
)
from pydantic import BaseModel, Field

__all__ = ["Seq", "Seqs", "SeqPost"]


class Seq(BaseModel):
    id: int = Field(..., gt=0)
    scan_id: int = Field(..., gt=0)
    name: str = ""
    data: str = ""

    @classmethod
    def from_sched_seq(cls, seq: sched_seq):
        return cls(
            id=seq.id,
            scan_id=seq.scan_id,
            name=seq.name,
            data=seq.data,
        )

    @classmethod
    def get(cls, seq_id: int):
        return Seq.from_sched_seq(sched_seq_get_by_id(seq_id))

    @classmethod
    def next(cls, seq_id: int, scan_id: int) -> Optional[Seq]:
        sched_seq = sched_seq_new(seq_id, scan_id)
        sched_seq = sched_seq_scan_next(sched_seq)
        if sched_seq is None:
            return None
        return Seq.from_sched_seq(sched_seq)

    @staticmethod
    def get_list() -> Seqs:
        return Seqs(__root__=[Seq.from_sched_seq(seq) for seq in sched_seq_get_all()])


class Seqs(BaseModel):
    __root__: List[Seq]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self) -> int:
        return len(list(self.__root__))


class SeqPost(BaseModel):
    name: str = ""
    data: str = ""
