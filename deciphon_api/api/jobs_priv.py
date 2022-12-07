from typing import Optional

import sqlalchemy.exc
from fastapi import APIRouter, Path, Query
from sqlmodel import Session
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH, ID
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.models import Job, JobState
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT


@router.patch(
    "/jobs/{job_id}/state", response_model=Job, status_code=OK, dependencies=AUTH
)
async def set_job_state(
    job_id: int = ID(),
    state: JobState = Query(...),
    error: Optional[str] = Query(None),
):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        job.state = state
        job.error = error
        session.add(job)
        session.commit()
        session.refresh(job)
        return job


@router.delete("/jobs/{job_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_job(job_id: int = ID()):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        session.delete(job)
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise ConflictException(str(e.orig))


@router.patch(
    "/jobs/{job_id}/progress/increment/{value}",
    response_model=Job,
    status_code=OK,
    dependencies=AUTH,
)
async def increment_progress(
    job_id: int = ID(),
    value: int = Path(..., ge=0, le=100),
):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        job.progress = min(100, job.progress + value)
        session.add(job)
        session.commit()
        session.refresh(job)
        return job
