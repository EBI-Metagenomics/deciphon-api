from typing import List

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import UnauthorizedError
from deciphon_api.models.hmm import HMM, HMMIDType
from deciphon_api.models.job import Job, JobProgressPatch, JobStatePatch
from deciphon_api.models.scan import Scan, ScanIDType

router = APIRouter()


@router.get(
    "/jobs/next_pend",
    summary="get next pending job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-next-pend-job",
)
def get_next_pend_job():
    return Job.next_pend()


@router.get(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-job",
)
def get_job(job_id: int = Path(..., gt=0)):
    return Job.get(job_id)


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

    return Job.set_state(job_id, job_patch)


@router.patch(
    "/jobs/{job_id}/progress",
    summary="patch job progress",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:increment-job-progress",
)
def increment_job_progress(
    job_id: int = Path(..., gt=0),
    job_patch: JobProgressPatch = Body(...),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    Job.increment_progress(job_id, job_patch.increment)
    return Job.get(job_id)


@router.get(
    "/jobs/{job_id}/hmm",
    summary="get hmm",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-hmm",
)
def get_hmm(job_id: int = Path(..., gt=0)):
    return HMM.get(job_id, HMMIDType.JOB_ID)


@router.get(
    "/jobs/{job_id}/scan",
    summary="get scan",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-scan",
)
def get_scan(job_id: int = Path(..., gt=0)):
    return Scan.get(job_id, ScanIDType.JOB_ID)


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
