from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .rc import RC, Code, ReturnData
from .seq import Seq


@app.get(
    "/jobs/{job_id}/seqs/next/{seq_id}",
    summary="get next sequence",
    response_model=Seq,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_jobs_xxx_seqs_next_yyy(job_id: int, seq_id: int):
    cseq = ffi.new("struct sched_seq *")
    cseq[0].id = seq_id
    cseq[0].job_id = job_id
    rc = RC(lib.sched_seq_next(cseq))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "next sequence not found")

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return Seq.from_cdata(cseq)
