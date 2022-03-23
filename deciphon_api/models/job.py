from enum import Enum
from typing import List

from pydantic import BaseModel, Field
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import EINVALException, create_exception
from deciphon_api.models.prod import Prod
from deciphon_api.models.seq import Seq
from deciphon_api.rc import RC

__all__ = ["Job", "JobPatch"]


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
    exec_started: int = Field(..., gt=0)
    exec_ended: int = Field(..., gt=0)

    @classmethod
    def from_cdata(cls, cjob):
        return cls(
            id=int(cjob.id),
            type=int(cjob.db_id),
            state=ffi.string(cjob.state).decode(),
            progress=int(cjob.db_id),
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
            raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return Job.from_cdata(ptr[0])

    def prods(self) -> List[Prod]:
        ptr = ffi.new("struct sched_prod *")
        prods: List[Prod] = []

        prods_hdl = ffi.new_handle(prods)
        rc = RC(lib.sched_job_get_prods(self.id, lib.append_prod, ptr, prods_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return prods

    def seqs(self) -> List[Seq]:
        ptr = ffi.new("struct sched_seq *")
        seqs: List[Seq] = []

        seqs_hdl = ffi.new_handle(seqs)
        rc = RC(lib.sched_job_get_seqs(self.id, lib.append_seq, ptr, seqs_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return seqs


class JobPatch(BaseModel):
    state: JobState = JobState.pend
    error: str = ""
