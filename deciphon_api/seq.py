from pydantic import BaseModel

from .csched import ffi

__all__ = ["Seq"]


class Seq(BaseModel):
    id: int = 0
    job_id: int = 0
    name: str = ""
    data: str = ""

    @classmethod
    def from_cdata(cls, cseq):
        return cls(
            id=int(cseq[0].id),
            job_id=int(cseq[0].job_id),
            name=ffi.string(cseq[0].name).decode(),
            data=ffi.string(cseq[0].data).decode(),
        )


@ffi.def_extern()
def append_seq_callback(cseq, arg):
    seqs = ffi.from_handle(arg)
    seqs.append(Seq.from_cdata(cseq))
