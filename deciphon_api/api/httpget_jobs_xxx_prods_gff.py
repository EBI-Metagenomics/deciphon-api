from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .._types import ErrorResponse
from ..exception import EINVALException
from ..job import Job, JobState

router = APIRouter()


@router.get(
    "/jobs/{job_id}/prods/gff",
    summary="get products as gff",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_xxx_prods_gff(job_id: int):
    job = Job.from_id(job_id)

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return job.result().gff()
