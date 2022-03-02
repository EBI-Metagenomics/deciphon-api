from fastapi.responses import PlainTextResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from ._types import ErrorResponse, FastaType
from .exception import EINVALException
from .job import Job, JobState


@app.get(
    "/jobs/{job_id}/prods/fasta/{fasta_type}",
    summary="get products as codon sequences",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_xxx_prods_fasta_yyy(job_id: int, fasta_type: FastaType):
    job = Job.from_id(job_id)

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return job.result().fasta(fasta_type.name)
