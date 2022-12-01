from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from deciphon_sched.job import (
    sched_job,
    sched_job_get_all,
    sched_job_get_by_id,
    sched_job_increment_progress,
    sched_job_next_pend,
    sched_job_remove,
    sched_job_set_done,
    sched_job_set_fail,
    sched_job_set_run,
    sched_job_state,
)
from pydantic import BaseModel, validator
from sqlmodel import Field, SQLModel

__all__ = [
    "Job",
    "JobStatePatch",
    "JobProgressPatch",
    "DoneJob",
    "PendJob",
    "JobRead",
    "JobCreate",
    "JobType",
]


class JobType(Enum):
    hmm = "hmm"
    press = "press"


class State(Enum):
    pend = "pend"
    run = "run"
    done = "done"
    fail = "fail"


class JobState(str, Enum):
    SCHED_PEND = "pend"
    SCHED_RUN = "run"
    SCHED_DONE = "done"
    SCHED_FAIL = "fail"

    @classmethod
    def from_sched_job_state(cls, job_state: sched_job_state):
        return cls[job_state.name]


class JobBase(SQLModel):
    type: JobType

    state: State = State.pend
    progress: int = Field(default=0, ge=0, le=100)
    error: str = ""

    submission: datetime = Field(default_factory=datetime.now)
    exec_started: datetime = Field(default_factory=lambda: datetime.fromtimestamp(0))
    exec_ended: datetime = Field(default_factory=lambda: datetime.fromtimestamp(0))


class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True, gt=0)

    @classmethod
    def from_sched_job(cls, job: sched_job):
        return cls(
            id=job.id,
            type=job.type,
            state=JobState.from_sched_job_state(job.state),
            progress=job.progress,
            error=job.error,
            submission=datetime.fromtimestamp(job.submission),
            exec_started=datetime.fromtimestamp(job.exec_started),
            exec_ended=datetime.fromtimestamp(job.exec_ended),
        )

    @staticmethod
    def get(job_id: int) -> Job:
        return Job.from_sched_job(sched_job_get_by_id(job_id))

    @staticmethod
    def set_state(job_id: int, state_patch: JobStatePatch) -> Job:
        if state_patch.state == JobState.SCHED_RUN:
            sched_job_set_run(job_id)

        elif state_patch.state == JobState.SCHED_FAIL:
            sched_job_set_fail(job_id, state_patch.error)

        elif state_patch.state == JobState.SCHED_DONE:
            sched_job_set_done(job_id)

        return Job.get(job_id)

    @staticmethod
    def next_pend() -> Optional[Job]:
        sched_job = sched_job_next_pend()
        if sched_job is None:
            return None
        return PendJob.from_sched_job(sched_job)

    @staticmethod
    def increment_progress(job_id: int, progress: int):
        sched_job_increment_progress(job_id, progress)

    @staticmethod
    def remove(job_id: int):
        sched_job_remove(job_id)

    @staticmethod
    def get_list() -> List[Job]:
        return [Job.from_sched_job(job) for job in sched_job_get_all()]


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    id: int


class DoneJob(Job):
    @validator("state")
    @classmethod
    def check_state(cls, value):
        if value != JobState.SCHED_DONE:
            raise ValueError("job not in DONE state.")
        return value


class PendJob(Job):
    @validator("state")
    @classmethod
    def check_state(cls, value):
        if value != JobState.SCHED_PEND:
            raise ValueError("job not in PEND state.")
        return value


class JobStatePatch(BaseModel):
    state: JobState = JobState.SCHED_PEND
    error: str = ""


class JobProgressPatch(BaseModel):
    increment: int = Field(..., ge=0, le=100)
