from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from deciphon_api.core.errors import InternalError, NotFoundError
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

__all__ = ["Seq", "SeqPost"]


class Seq(BaseModel):
    id: int = Field(..., gt=0)
    scan_id: int = Field(..., gt=0)
    name: str = ""
    data: str = ""

    @classmethod
    def from_cdata(cls, cseq):
        return cls(
            id=int(cseq.id),
            scan_id=int(cseq.scan_id),
            name=ffi.string(cseq.name).decode(),
            data=ffi.string(cseq.data).decode(),
        )

    @classmethod
    def from_id(cls, seq_id: int):
        ptr = ffi.new("struct sched_seq *")

        rc = RC(lib.sched_seq_get_by_id(ptr, seq_id))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise NotFoundError("seq")

        if rc != RC.OK:
            raise InternalError(rc)

        return Seq.from_cdata(ptr[0])

    @classmethod
    def next(cls, seq_id: int, scan_id: int) -> List[Seq]:
        ptr = ffi.new("struct sched_seq *")

        cseq = ptr[0]
        cseq.id = seq_id
        cseq.scan_id = scan_id
        rc = RC(lib.sched_seq_scan_next(ptr))

        if rc == RC.END:
            return []

        if rc == RC.NOTFOUND:
            return []

        if rc != RC.OK:
            raise InternalError(rc)

        return [Seq.from_cdata(cseq)]

    @staticmethod
    def get_list() -> List[Seq]:
        ptr = ffi.new("struct sched_seq *")

        seqs: List[Seq] = []
        rc = RC(lib.sched_seq_get_all(lib.append_seq, ptr, ffi.new_handle(seqs)))
        assert rc != RC.END

        if rc != RC.OK:
            raise InternalError(rc)

        return seqs


class SeqPost(BaseModel):
    name: str = ""
    data: str = ""


@ffi.def_extern()
def append_seq(ptr, arg):
    seqs = ffi.from_handle(arg)
    seqs.append(Seq.from_cdata(ptr[0]))
