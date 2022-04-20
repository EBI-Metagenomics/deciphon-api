from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Union

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.hmm import sched_hmm
from deciphon_api.sched.rc import RC
from deciphon_api.sched.scan import sched_scan

__all__ = [
    "sched_job",
    "sched_job_get_by_id",
    "sched_job_get_all",
    "sched_job_set_run",
    "sched_job_set_fail",
    "sched_job_set_done",
    "sched_job_submit",
    "sched_job_add_progress",
    "sched_job_remove",
]


class sched_job_type(int, Enum):
    SCHED_SCAN = 0
    SCHED_HMM = 1


class sched_job_state(int, Enum):
    SCHED_PEND = 0
    SCHED_RUN = 1
    SCHED_DONE = 2
    SCHED_FAIL = 3

    @classmethod
    def from_cdata(cls, cstate):
        state = ffi.string(cstate).decode()
        if state == "pend":
            return cls(0)
        elif state == "run":
            return cls(1)
        elif state == "done":
            return cls(2)
        elif state == "fail":
            return cls(3)
        assert False


@dataclass
class sched_job:
    id: int
    type: sched_job_type

    state: sched_job_state
    progress: int
    error: str

    submission: int
    exec_started: int
    exec_ended: int

    ptr: Any

    def refresh(self):
        c = self.ptr[0]

        self.id = int(c.id)
        self.type = sched_job_type(int(c.type))

        self.state = sched_job_state.from_cdata(c.data)
        self.progress = int(c.progress)
        self.error = ffi.string(c.error).decode()

        self.submission = int(c.submission)
        self.exec_started = int(c.exec_started)
        self.exec_ended = int(c.exec_ended)


def possess(ptr) -> sched_job:
    c = ptr[0]
    return sched_job(
        int(c.id),
        sched_job_type(int(c.type)),
        sched_job_state.from_cdata(c.state),
        int(c.progress),
        ffi.string(c.error).decode(),
        int(c.submission),
        int(c.exec_started),
        int(c.exec_ended),
        ptr,
    )


def sched_job_new(job_type: sched_job_type) -> sched_job:
    ptr = ffi.new("struct sched_job *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    lib.sched_job_init(ptr, job_type)
    return possess(ptr)


def new_job() -> sched_job:
    ptr = ffi.new("struct sched_job *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    lib.sched_job_init(ptr, sched_job_type.SCHED_SCAN)
    return possess(ptr)


def sched_job_get_by_id(job_id: int) -> sched_job:
    ptr = new_job().ptr
    rc = RC(lib.sched_job_get_by_id(ptr, job_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_job_next_pend():
    ptr = new_job().ptr
    rc = RC(lib.sched_job_next_pend(ptr))
    rc.raise_for_status()
    return possess(ptr)


def sched_job_get_all() -> List[sched_job]:
    jobs: List[sched_job] = []
    ptr = new_job().ptr
    rc = RC(lib.sched_job_get_all(lib.append_job, ptr, ffi.new_handle(jobs)))
    rc.raise_for_status()
    return jobs


def sched_job_set_run(job_id: int):
    rc = RC(lib.sched_job_set_run(job_id))
    rc.raise_for_status()


def sched_job_set_fail(job_id: int, msg: str):
    rc = RC(lib.sched_job_set_fail(job_id, msg.encode()))
    rc.raise_for_status()


def sched_job_set_done(job_id: int):
    rc = RC(lib.sched_job_set_done(job_id))
    rc.raise_for_status()


def sched_job_submit(actual_job: Union[sched_hmm, sched_scan]):
    if isinstance(actual_job, sched_hmm):
        ptr = sched_job_new(sched_job_type.SCHED_HMM).ptr
    else:
        assert isinstance(actual_job, sched_scan)
        ptr = sched_job_new(sched_job_type.SCHED_SCAN)

    rc = RC(lib.sched_job_submit(ptr, actual_job.ptr))
    rc.raise_for_status()

    actual_job.refresh()


def sched_job_add_progress(job_id: int, progress: int):
    rc = RC(lib.sched_job_add_progress(job_id, progress))
    rc.raise_for_status()


def sched_job_remove(job_id: int):
    rc = RC(lib.sched_job_remove(job_id))
    rc.raise_for_status()


@ffi.def_extern()
def append_job(ptr, arg):
    sched_jobs = ffi.from_handle(arg)
    sched_jobs.append(possess(ptr))
