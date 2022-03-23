from typing import List

from fastapi import APIRouter
from starlette.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import EINVALException, ErrorResponse, create_exception
from deciphon_api.models.job import Job, JobPatch, JobState
from deciphon_api.rc import RC

router = APIRouter()


@router.get(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="jobs:get-job",
)
def get_job(job_id: int):
    return Job.from_id(job_id)


@router.get(
    "/jobs/next_pend",
    summary="get next pending job",
    response_model=List[Job],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="jobs:get-next-job",
)
def get_next_job():
    cjob = ffi.new("struct sched_job *")

    rc = RC(lib.sched_job_next_pend(cjob))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return [Job.from_cdata(cjob)]


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
    name="jobs:change-job-state",
)
def change_job_state(job_id: int, job_patch: JobPatch):
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
