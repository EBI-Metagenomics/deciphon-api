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
from ..job import Job, JobPatch, JobState
from ..rc import RC

router = APIRouter()


@router.patch(
    "/jobs/{job_id}",
    summary="patch job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppatch_jobs_xxx(job_id: int, job_patch: JobPatch):
    job = Job.from_id(job_id)

    if job.state == job_patch.state:
        raise EINVALException(HTTP_403_FORBIDDEN, "redundant job state update")

    if job.state == JobState.pend and job_patch.state == JobState.run:

        rc = RC(lib.sched_job_set_run(job_id))

    elif job.state == JobState.run and job_patch.state == JobState.done:

        rc = RC(lib.sched_job_set_done(job_id))

    elif job.state == JobState.run and job_patch.state == JobState.fail:

        rc = RC(lib.sched_job_set_fail(job_id, job_patch.error.encode()))

    else:
        raise EINVALException(HTTP_403_FORBIDDEN, "invalid job state update")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return Job.from_id(job_id)
