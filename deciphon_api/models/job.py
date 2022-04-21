from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from deciphon_api.sched.job import (
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

__all__ = ["Job", "JobStatePatch", "JobProgressPatch"]


class JobState(str, Enum):
    SCHED_PEND = "pend"
    SCHED_RUN = "run"
    SCHED_DONE = "done"
    SCHED_FAIL = "fail"

    @classmethod
    def from_sched_job_state(cls, job_state: sched_job_state):
        return cls[job_state.name]


class Job(BaseModel):
    id: int = Field(..., gt=0)
    type: int = Field(..., ge=0, le=1)

    state: JobState = JobState.SCHED_PEND
    progress: int = Field(..., ge=0, le=100)
    error: str = ""

    submission: int = Field(..., gt=0)
    exec_started: int = Field(..., ge=0)
    exec_ended: int = Field(..., ge=0)

    @classmethod
    def from_sched_job(cls, job: sched_job):
        return cls(
            id=job.id,
            type=job.type,
            state=JobState.from_sched_job_state(job.state),
            progress=job.progress,
            error=job.error,
            submission=job.submission,
            exec_started=job.exec_started,
            exec_ended=job.exec_ended,
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
    def next_pend() -> Job:
        return Job.from_sched_job(sched_job_next_pend())

    def assert_state(self, state: JobState):
        pass
        # if self.state != state:
        #     raise ConditionError(f"job not in {str(state.done)} state")

    @staticmethod
    def increment_progress(job_id: int, progress: int):
        sched_job_increment_progress(job_id, progress)

    @staticmethod
    def remove(job_id: int):
        sched_job_remove(job_id)

    @staticmethod
    def get_list() -> List[Job]:
        return [Job.from_sched_job(job) for job in sched_job_get_all()]


class JobStatePatch(BaseModel):
    state: JobState = JobState.SCHED_PEND
    error: str = ""


class JobProgressPatch(BaseModel):
    increment: int = Field(..., ge=0, le=100)
