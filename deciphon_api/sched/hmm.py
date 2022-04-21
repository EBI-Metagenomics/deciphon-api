from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.rc import RC

__all__ = [
    "sched_hmm",
    "sched_hmm_new",
    "sched_hmm_get_all",
    "sched_hmm_get_by_filename",
    "sched_hmm_get_by_id",
    "sched_hmm_get_by_job_id",
    "sched_hmm_get_by_xxh3",
    "sched_hmm_remove",
]


@dataclass
class sched_hmm:
    id: int
    xxh3: int
    filename: str
    job_id: int
    ptr: Any

    def refresh(self):
        c = self.ptr[0]

        self.id = int(c.id)
        self.xxh3 = int(c.xxh3)

        self.filename = ffi.string(c.filename)
        self.job_id = int(c.job_id)


def string(cdata) -> str:
    return ffi.string(cdata).decode()


def possess(ptr) -> sched_hmm:
    c = ptr[0]
    return sched_hmm(int(c.id), int(c.xxh3), string(c.filename), int(c.job_id), ptr)


def new_hmm():
    ptr = ffi.new("struct sched_hmm *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    lib.sched_hmm_init(ptr)
    return ptr


def sched_hmm_new(filename: str) -> sched_hmm:
    ptr = new_hmm()
    rc = RC(lib.sched_hmm_set_file(ptr, filename.encode()))
    rc.raise_for_status()
    return possess(ptr)


def sched_hmm_get_by_id(hmm_id: int) -> sched_hmm:
    ptr = new_hmm()
    rc = RC(lib.sched_hmm_get_by_id(ptr, hmm_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_hmm_get_by_job_id(hmm_id: int) -> sched_hmm:
    ptr = new_hmm()
    rc = RC(lib.sched_hmm_get_by_job_id(ptr, hmm_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_hmm_get_by_xxh3(xxh3: int) -> sched_hmm:
    ptr = new_hmm()
    rc = RC(lib.sched_hmm_get_by_xxh3(ptr, xxh3))
    rc.raise_for_status()
    return possess(ptr)


def sched_hmm_get_by_filename(filename: str) -> sched_hmm:
    ptr = new_hmm()
    rc = RC(lib.sched_hmm_get_by_filename(ptr, filename.encode()))
    rc.raise_for_status()
    return possess(ptr)


def sched_hmm_get_all() -> List[sched_hmm]:
    hmms: List[sched_hmm] = []
    ptr = new_hmm()
    rc = RC(lib.sched_hmm_get_all(lib.append_hmm, ptr, ffi.new_handle(hmms)))
    rc.raise_for_status()
    return hmms


def sched_hmm_remove(hmm_id: int):
    rc = RC(lib.sched_hmm_remove(hmm_id))
    rc.raise_for_status()


@ffi.def_extern()
def append_hmm(ptr, arg):
    sched_hmms = ffi.from_handle(arg)
    sched_hmms.append(possess(ptr))
