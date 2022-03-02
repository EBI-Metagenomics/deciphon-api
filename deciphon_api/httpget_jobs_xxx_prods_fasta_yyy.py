from fastapi.responses import PlainTextResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from ._types import FastaType
from .exception import DCPException
from .job import Job, JobState
from .rc import StrRC
from .response import ErrorResponse


@app.get(
    "/jobs/{job_id}/prods/fasta/{fasta_type}",
    summary="get products as codon sequences",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_xxx_prods_fasta_yyy(job_id: int, fasta_type: FastaType):
    job = Job.from_id(job_id)

    if job.state != JobState.done:
        raise DCPException(
            HTTP_404_NOT_FOUND,
            StrRC.EINVAL,
            f"invalid job state ({job.state}) for the request",
        )

    return job.result().fasta(fasta_type.name)
