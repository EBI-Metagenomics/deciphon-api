from fastapi import APIRouter
from starlette.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .._types import ErrorResponse
from ..csched import lib
from ..exception import EINVALException, create_exception
from ..job import Job, JobState
from ..rc import RC

router = APIRouter()


@router.patch(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppatch_jobs_xxx(job_id: int, state: JobState, error: str):
    job = Job.from_id(job_id)

    if job.state == state:
        raise EINVALException(HTTP_403_FORBIDDEN, "redundant job state update")

    if job.state == JobState.pend and state == JobState.run:

        rc = RC(lib.sched_job_set_run(job_id))

    elif job.state == JobState.run and state == JobState.done:

        rc = RC(lib.sched_job_set_done(job_id))

    elif job.state == JobState.run and state == JobState.fail:

        rc = RC(lib.sched_job_set_fail(job_id, error.encode()))

    else:
        raise EINVALException(HTTP_403_FORBIDDEN, "invalid job state update")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return Job.from_id(job_id)
