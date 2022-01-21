from pydantic import BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .rc import Code, RC, ReturnData

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


@app.get(
    "/seqs/{seq_id}",
    summary="get sequence",
    response_model=Seq,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_seq(seq_id: int):
    cseq = ffi.new("struct sched_seq *")
    cseq[0].id = seq_id

    rc = RC(lib.sched_seq_get(cseq))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "sequence not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return Seq.from_cdata(cseq)
