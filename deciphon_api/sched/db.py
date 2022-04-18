from dataclasses import dataclass
from typing import Any, List

from deciphon_api.core.errors import ConstraintError, InternalError, NotFoundError
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

__all__ = [
    "sched_db_add",
    "sched_db_get_all",
    "sched_db_get_by_filename",
    "sched_db_get_by_hmm_id",
    "sched_db_get_by_id",
    "sched_db_get_by_xxh3",
    "sched_db_remove",
]


@dataclass
class sched_db:
    id: int
    xxh3: int
    filename: str
    hmm_id: int
    ptr: Any


def possess(ptr):
    c = ptr[0]
    return sched_db(
        int(c.id), int(c.xxh3), ffi.string(c.filename).decode(), int(c.hmm_id), ptr
    )


def sched_db_add(filename: str) -> sched_db:
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_add(ptr, filename.encode()))
    if rc != RC.OK:
        raise InternalError(rc)

    return possess(ptr)


def sched_db_remove(db_id: int):
    rc = RC(lib.sched_db_remove(db_id))
    if rc == RC.NOTFOUND:
        raise NotFoundError("database")

    if rc == RC.ECONSTRAINT:
        raise ConstraintError("can't remove referenced database")

    if rc != RC.OK:
        raise InternalError(rc)


def sched_db_get_by_id(db_id: int) -> sched_db:
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_get_by_id(ptr, db_id))
    if rc == RC.NOTFOUND:
        raise NotFoundError("database")
    return possess(ptr)


def sched_db_get_by_xxh3(xxh3: int) -> sched_db:
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_get_by_xxh3(ptr, xxh3))
    if rc == RC.NOTFOUND:
        raise NotFoundError("database")
    return possess(ptr)


def sched_db_get_by_filename(filename: str) -> sched_db:
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_get_by_filename(ptr, filename.encode()))
    if rc == RC.NOTFOUND:
        raise NotFoundError("database")
    return possess(ptr)


def sched_db_get_by_hmm_id(hmm_id: int) -> sched_db:
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_get_by_hmm_id(ptr, hmm_id))
    if rc == RC.NOTFOUND:
        raise NotFoundError("database")
    return possess(ptr)


def sched_db_get_all() -> List[sched_db]:
    dbs: List[sched_db] = []
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_get_all(lib.append_db, ptr, ffi.new_handle(dbs)))
    if rc != RC.OK:
        raise InternalError(rc)
    return dbs


@ffi.def_extern()
def append_db(ptr, arg):
    sched_dbs = ffi.from_handle(arg)
    sched_dbs.append(possess(ptr))
