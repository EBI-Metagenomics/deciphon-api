from typing import List

from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .rc import RC, StrRC
from .response import ErrorResponse
from .seq import Seq


@app.get(
    "/jobs/{job_id}/seqs",
    summary="get all sequences of a job",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_xxx_seqs(job_id: int):
    cseq = ffi.new("struct sched_seq *")
    seqs: List[Seq] = []

    rc = RC(lib.sched_job_get_seqs(job_id, lib.seq_set_cb, cseq, ffi.new_handle(seqs)))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "job not found")

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return seqs
