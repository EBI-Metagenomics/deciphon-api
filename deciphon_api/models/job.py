from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from deciphon_api.core.errors import (
    ConditionError,
    ConstraintError,
    InternalError,
    NotFoundError,
)
from deciphon_api.models.prod import Prod
from deciphon_api.models.seq import Seq
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

__all__ = ["Job", "JobStatePatch", "JobProgressPatch"]


class JobState(str, Enum):
    pend = "pend"
    run = "run"
    done = "done"
    fail = "fail"


class Job(BaseModel):
    id: int = Field(..., gt=0)
    type: int = Field(..., ge=0, le=1)

    state: JobState = JobState.pend
    progress: int = Field(..., ge=0, le=100)
    error: str = ""

    submission: int = Field(..., gt=0)
    exec_started: int = Field(..., ge=0)
    exec_ended: int = Field(..., ge=0)

    @classmethod
    def from_cdata(cls, cjob):
        return cls(
            id=int(cjob.id),
            type=int(cjob.type),
            state=ffi.string(cjob.state).decode(),
            progress=int(cjob.progress),
            error=ffi.string(cjob.error).decode(),
            submission=int(cjob.submission),
            exec_started=int(cjob.exec_started),
            exec_ended=int(cjob.exec_ended),
        )

    @classmethod
    def from_id(cls, job_id: int):
        ptr = ffi.new("struct sched_job *")

        rc = RC(lib.sched_job_get_by_id(ptr, job_id))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise NotFoundError("job")

        if rc != RC.OK:
            raise InternalError(rc)

        return Job.from_cdata(ptr[0])

    def prods(self) -> List[Prod]:
        ptr = ffi.new("struct sched_prod *")
        prods: List[Prod] = []

        prods_hdl = ffi.new_handle(prods)
        rc = RC(lib.sched_job_get_prods(self.id, lib.append_prod, ptr, prods_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise NotFoundError("job")

        if rc != RC.OK:
            raise InternalError(rc)

        return prods

    def seqs(self) -> List[Seq]:
        ptr = ffi.new("struct sched_seq *")
        seqs: List[Seq] = []

        seqs_hdl = ffi.new_handle(seqs)
        rc = RC(lib.sched_job_get_seqs(self.id, lib.append_seq, ptr, seqs_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise NotFoundError("job")

        if rc != RC.OK:
            raise InternalError(rc)

        return seqs

    def assert_state(self, state: JobState):
        if self.state != state:
            raise ConditionError(f"job not in {str(state.done)} state")

    @staticmethod
    def add_progress(job_id: int, progress: int):
        rc = RC(lib.sched_job_add_progress(job_id, progress))

        if rc == RC.NOTFOUND:
            raise NotFoundError("job")

        if rc != RC.OK:
            raise InternalError(rc)

    @staticmethod
    def remove(job_id: int):
        rc = RC(lib.sched_job_remove(job_id))

        if rc == RC.NOTFOUND:
            raise NotFoundError("job")

        if rc == RC.ECONSTRAINT:
            raise ConstraintError("can't remove referenced job")

        if rc != RC.OK:
            raise InternalError(rc)

    @staticmethod
    def get_list() -> List[Job]:
        ptr = ffi.new("struct sched_job *")

        jobs: List[Job] = []
        rc = RC(lib.sched_job_get_all(lib.append_job, ptr, ffi.new_handle(jobs)))
        assert rc != RC.END

        if rc != RC.OK:
            raise InternalError(rc)

        return jobs


class JobStatePatch(BaseModel):
    state: JobState = JobState.pend
    error: str = ""


class JobProgressPatch(BaseModel):
    add_progress: int = Field(..., ge=0, le=100)


@ffi.def_extern()
def append_job(ptr, arg):
    jobs = ffi.from_handle(arg)
    jobs.append(Job.from_cdata(ptr[0]))
