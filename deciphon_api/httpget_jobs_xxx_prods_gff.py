from typing import List

from fastapi.responses import PlainTextResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .exception import DCPException
from .job import Job, JobResult, JobState
from .prod import Prod
from .rc import Code, ReturnData
from .seq import Seq


@app.get(
    "/jobs/{job_id}/prods/gff",
    summary="get products as gff",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def httpget_jobs_xxx_prods_gff(job_id: int):
    job = Job.from_id(job_id)

    if job.state != JobState.done:
        raise DCPException(
            HTTP_404_NOT_FOUND,
            Code.EINVAL,
            f"invalid job state ({job.state}) for the request",
        )

    prods: List[Prod] = job.prods()
    seqs: List[Seq] = job.seqs()
    return JobResult(job, prods, seqs).gff()
