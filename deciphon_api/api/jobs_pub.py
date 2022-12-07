from fastapi import APIRouter
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK

from deciphon_api.api.utils import ID
from deciphon_api.exceptions import NotFoundException
from deciphon_api.models import HMM, Job, JobState, Scan
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK


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
