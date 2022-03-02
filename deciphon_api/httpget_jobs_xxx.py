from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .job import Job
from ._types import ErrorResponse


@app.get(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_xxx(job_id: int):
    return Job.from_id(job_id)
