from pydantic import BaseModel, Field

from deciphon_api.csched import ffi

__all__ = ["Seq"]


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


@ffi.def_extern()
def append_seq(ptr, arg):
    seqs = ffi.from_handle(arg)
    seqs.append(Seq.from_cdata(ptr[0]))
