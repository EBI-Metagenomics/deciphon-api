from typing import List

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.hmms import download_hmm, get_hmm_by_job_id
from deciphon_api.api.responses import responses
from deciphon_api.api.scans import get_scan_by_job_id
from deciphon_api.models.hmm import HMM, HMMIDType
from deciphon_api.models.job import Job, JobProgressPatch, JobStatePatch
from deciphon_api.models.scan import Scan, ScanIDType

router = APIRouter()


@router.get(
    "/jobs/next-pend",
    summary="get next pending job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-next-pend-job",
)
async def get_next_pend_job():
    job = Job.next_pend()
    if job is None:
        return Response(status_code=HTTP_204_NO_CONTENT)
    return job


@router.get(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-job",
)
async def get_job(job_id: int = Path(..., gt=0)):
    return Job.get(job_id)


@router.get(
    "/jobs",
    summary="get job list",
    response_model=List[Job],
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-job-list",
)
async def get_job_list():
    return Job.get_list()


@router.patch(
    "/jobs/{job_id}/state",
    summary="patch job state",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:set-job-state",
    dependencies=[Depends(auth_request)],
)
async def set_job_state(
    job_id: int = Path(..., gt=0),
    job_patch: JobStatePatch = Body(...),
):
    return Job.set_state(job_id, job_patch)


@router.patch(
    "/jobs/{job_id}/progress",
    summary="patch job progress",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:increment-job-progress",
    dependencies=[Depends(auth_request)],
)
async def increment_job_progress(
    job_id: int = Path(..., gt=0),
    job_patch: JobProgressPatch = Body(...),
):
    Job.increment_progress(job_id, job_patch.increment)
    return Job.get(job_id)


@router.get(
    "/jobs/{job_id}/hmm",
    summary="get hmm",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-hmm",
    deprecated=True,
)
async def get_hmm(job_id: int = Path(..., gt=0)):
    return HMM.get(job_id, HMMIDType.JOB_ID)


get_hmm_by_job_id = router.get(
    "/jobs/{job_id}/hmm",
    summary="get hmm by job_id",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-hmm-by-job-id",
)(get_hmm_by_job_id)


download_hmm = router.get(
    "/jobs/{job_id}/hmm/download",
    summary="download hmm",
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:download-hmm",
)(download_hmm)


@router.get(
    "/jobs/{job_id}/scan",
    summary="get scan",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-scan",
    deprecated=True,
)
async def get_scan(job_id: int = Path(..., gt=0)):
    return Scan.get(job_id, ScanIDType.JOB_ID)


get_scan_by_job_id = router.get(
    "/jobs/{job_id}/scan",
    summary="get scan by job_id",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:get-scan-by-job-id",
)(get_scan_by_job_id)


@router.delete(
    "/jobs/{job_id}",
    summary="remove job",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="jobs:remove-job",
    dependencies=[Depends(auth_request)],
)
async def remove_job(job_id: int = Path(..., gt=0)):
    Job.remove(job_id)
    return JSONResponse({})
