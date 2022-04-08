from typing import List

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import ForbiddenError, InternalError, UnauthorizedError
from deciphon_api.models.hmm import HMM
from deciphon_api.models.job import Job, JobProgressPatch, JobState, JobStatePatch
from deciphon_api.models.scan import Scan
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

router = APIRouter()


@router.get(
    "/jobs/next_pend",
    summary="get next pending job",
    response_model=List[Job],
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-next-pend-job",
)
def get_next_pend_job():
    ptr = ffi.new("struct sched_job *")

    rc = RC(lib.sched_job_next_pend(ptr))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise InternalError(rc)

    return [Job.from_cdata(ptr[0])]


@router.get(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-job",
)
def get_job(job_id: int = Path(..., gt=0)):
    return Job.from_id(job_id)


@router.get(
    "/jobs",
    summary="get job list",
    response_model=List[Job],
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-job-list",
)
def get_job_list():
    return Job.get_list()


@router.patch(
    "/jobs/{job_id}/state",
    summary="patch job state",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:set-job-state",
)
def set_job_state(
    job_id: int = Path(..., gt=0),
    job_patch: JobStatePatch = Body(...),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    job = Job.from_id(job_id)

    if job.state == job_patch.state:
        raise ForbiddenError("redundant job state update")

    if job.state == JobState.pend and job_patch.state == JobState.run:

        rc = RC(lib.sched_job_set_run(job_id))

    elif job.state == JobState.run and job_patch.state == JobState.done:

        rc = RC(lib.sched_job_set_done(job_id))

    elif job.state == JobState.run and job_patch.state == JobState.fail:

        rc = RC(lib.sched_job_set_fail(job_id, job_patch.error.encode()))

    else:
        raise ForbiddenError("invalid job state update")

    if rc != RC.OK:
        raise InternalError(rc)

    return Job.from_id(job_id)


@router.patch(
    "/jobs/{job_id}/progress/add",
    summary="patch job progress",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:add-job-progress",
)
def add_job_progress(
    job_id: int = Path(..., gt=0),
    job_patch: JobProgressPatch = Body(...),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    Job.add_progress(job_id, job_patch.add_progress)
    return Job.from_id(job_id)


@router.get(
    "/jobs/{job_id}/hmm",
    summary="get hmm",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-hmm",
)
def get_hmm(job_id: int = Path(..., gt=0)):
    return HMM.get_by_job_id(job_id)


@router.get(
    "/jobs/{job_id}/scan",
    summary="get scan",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-scan",
)
def get_scan(job_id: int = Path(..., gt=0)):
    return Scan.get_by_job_id(job_id)


@router.delete(
    "/jobs/{job_id}",
    summary="remove job",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:remove-job",
)
def remove_job(
    job_id: int = Path(..., gt=0), authenticated: bool = Depends(auth_request)
):
    if not authenticated:
        raise UnauthorizedError()

    Job.remove(job_id)
    return JSONResponse({})
