from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from deciphon_api.sched.seq import (
    sched_seq,
    sched_seq_get_all,
    sched_seq_get_by_id,
    sched_seq_new,
    sched_seq_scan_next,
)

__all__ = ["Seq", "SeqPost"]


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
    def next(cls, seq_id: int, scan_id: int) -> Seq:
        seq = sched_seq_new(seq_id, scan_id)
        sched_seq_scan_next(seq)
        return Seq.from_sched_seq(seq)

    @staticmethod
    def get_list() -> List[Seq]:
        return [Seq.from_sched_seq(seq) for seq in sched_seq_get_all()]


class SeqPost(BaseModel):
    name: str = ""
    data: str = ""
