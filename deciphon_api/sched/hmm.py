from dataclasses import dataclass
from typing import Any, List

from deciphon_api.core.errors import ConstraintError, InternalError, NotFoundError
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

__all__ = [
    "sched_hmm",
    "sched_db_add",
    "sched_hmm_remove",
    "sched_hmm_get_by_id",
    "sched_hmm_get_by_xxh3",
    "sched_hmm_get_by_job_id",
    "sched_hmm_get_by_filename",
    "sched_hmm_get_all",
    "sched_hmm_to_db_filename",
]


@dataclass
class sched_hmm:
    id: int
    xxh3: int
    filename: str
    job_id: int
    ptr: Any


def possess(ptr):
    c = ptr[0]
    return sched_hmm(
        int(c.id), int(c.xxh3), ffi.string(c.filename).decode(), int(c.job_id), ptr
    )


def sched_db_add(filename: str) -> sched_hmm:
    ptr = ffi.new("struct sched_hmm *")
    rc = RC(lib.sched_hmm_add(ptr, filename.encode()))
    if rc != RC.OK:
        raise InternalError(rc)

    return possess(ptr)


def sched_hmm_remove(hmm_id: int):
    rc = RC(lib.sched_hmm_remove(hmm_id))
    if rc == RC.NOTFOUND:
        raise NotFoundError("hmm")

    if rc == RC.ECONSTRAINT:
        raise ConstraintError("can't remove referenced hmm")

    if rc != RC.OK:
        raise InternalError(rc)


def sched_hmm_get_by_id(hmm_id: int) -> sched_hmm:
    ptr = ffi.new("struct sched_hmm *")
    rc = RC(lib.sched_hmm_get_by_id(ptr, hmm_id))
    if rc == RC.NOTFOUND:
        raise NotFoundError("hmm")
    return possess(ptr)


def sched_hmm_get_by_xxh3(xxh3: int) -> sched_hmm:
    ptr = ffi.new("struct sched_hmm *")
    rc = RC(lib.sched_hmm_get_by_xxh3(ptr, xxh3))
    if rc == RC.NOTFOUND:
        raise NotFoundError("hmm")
    return possess(ptr)


def sched_hmm_get_by_filename(filename: str) -> sched_hmm:
    ptr = ffi.new("struct sched_hmm *")
    rc = RC(lib.sched_hmm_get_by_filename(ptr, filename.encode()))
    if rc == RC.NOTFOUND:
        raise NotFoundError("hmm")
    return possess(ptr)


def sched_hmm_get_by_job_id(hmm_id: int) -> sched_hmm:
    ptr = ffi.new("struct sched_hmm *")
    rc = RC(lib.sched_hmm_get_by_job_id(ptr, hmm_id))
    if rc == RC.NOTFOUND:
        raise NotFoundError("hmm")
    return possess(ptr)


def sched_hmm_get_all() -> List[sched_hmm]:
    hmms: List[sched_hmm] = []
    ptr = ffi.new("struct sched_hmm *")
    rc = RC(lib.sched_hmm_get_all(lib.append_hmm, ptr, ffi.new_handle(hmms)))
    if rc != RC.OK:
        raise InternalError(rc)
    return hmms


def sched_hmm_to_db_filename(filename: str) -> str:
    name = filename.encode()
    lib.sched_hmm_to_db_filename(name)
    return name.decode()
