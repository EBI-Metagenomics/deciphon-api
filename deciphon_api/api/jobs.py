from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH
from deciphon_api.errors import NotFoundInDBError
from deciphon_api.models import Job, JobRead, JobUpdate
from deciphon_api.sched import Sched, select

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT


@router.get("/jobs", response_model=List[JobRead], status_code=OK)
async def read_jobs():
    with Sched() as sched:
        return sched.exec(select(Job)).all()


@router.get("/jobs/{job_id}", response_model=JobRead, status_code=OK)
async def read_job(job_id: int):
    with Sched() as sched:
        job = sched.get(Job, job_id)
        if not job:
            raise NotFoundInDBError("Job")
        return job


@router.patch(
    "/jobs/{job_id}", response_model=JobRead, status_code=OK, dependencies=AUTH
)
async def update_job(job_id: int, job: JobUpdate):
    with Sched() as sched:
        x = sched.get(Job, job_id)
        if not x:
            raise NotFoundInDBError("Job")
        for key, value in job.dict(exclude_unset=True).items():
            setattr(x, key, value)
        sched.add(x)
        sched.commit()
        sched.refresh(x)
        return JobRead.parse_obj(x)


@router.delete("/jobs/{job_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_job(job_id: int):
    with Sched() as sched:
        job = sched.get(Job, job_id)
        if not job:
            raise NotFoundInDBError("Job")
        sched.delete(job)
        sched.commit()
