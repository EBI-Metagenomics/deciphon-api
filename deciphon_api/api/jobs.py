from datetime import datetime
from typing import Optional

import sqlalchemy.exc
from fastapi import APIRouter, Path, Query
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH, ID
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.models import HMM, Job, JobState, Scan
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT


@router.get("/jobs", response_model=list[Job], status_code=OK)
async def get_jobs():
    with Session(get_sched()) as session:
        return session.exec(select(Job)).all()


@router.get("/jobs/next-pend", response_model=Job, status_code=OK)
async def get_next_pend_job():
    with Session(get_sched()) as session:
        stmt = select(Job).where(Job.state == JobState.pend)
        job = session.exec(stmt).first()
        if not job:
            raise NotFoundException(Job)
        return job


@router.get("/jobs/{job_id}", response_model=Job, status_code=OK)
async def get_job_by_id(job_id: int = ID()):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        return job


@router.get("/jobs/{job_id}/hmm", response_model=HMM, status_code=OK)
async def get_job_hmm(job_id: int = ID()):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        return job.hmm


@router.get("/jobs/{job_id}/scan", response_model=Scan, status_code=OK)
async def get_job_scan(job_id: int = ID()):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        return job.scan


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
        if job.progress < 100:
            # It is truly done (from user's point of view)
            # when the job payload has been stored by
            # another API call.
            job.progress = min(99, job.progress + value)
            session.add(job)
            session.commit()
            session.refresh(job)
        return job


@router.patch(
    "/jobs/{job_id}/set-run",
    response_model=Job,
    status_code=OK,
    dependencies=AUTH,
)
async def set_run(
    job_id: int = ID(),
):
    with Session(get_sched()) as session:
        job = session.get(Job, job_id)
        if not job:
            raise NotFoundException(Job)
        job.state = JobState.run
        job.exec_started = datetime.now()
        session.add(job)
        session.commit()
        session.refresh(job)
        return job
