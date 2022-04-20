from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.rc import RC

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


def string(cdata) -> str:
    return ffi.string(cdata).decode()


def possess(ptr):
    c = ptr[0]
    return sched_db(int(c.id), int(c.xxh3), string(c.filename), int(c.hmm_id), ptr)


def new_db():
    ptr = ffi.new("struct sched_db *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    return ptr


def sched_db_add(filename: str) -> sched_db:
    ptr = new_db()
    rc = RC(lib.sched_db_add(ptr, filename.encode()))
    rc.raise_for_status()
    return possess(ptr)


def sched_db_remove(db_id: int):
    rc = RC(lib.sched_db_remove(db_id))
    rc.raise_for_status()


def sched_db_get_by_id(db_id: int) -> sched_db:
    ptr = new_db()
    rc = RC(lib.sched_db_get_by_id(ptr, db_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_db_get_by_xxh3(xxh3: int) -> sched_db:
    ptr = new_db()
    rc = RC(lib.sched_db_get_by_xxh3(ptr, xxh3))
    rc.raise_for_status()
    return possess(ptr)


def sched_db_get_by_filename(filename: str) -> sched_db:
    ptr = new_db()
    rc = RC(lib.sched_db_get_by_filename(ptr, filename.encode()))
    rc.raise_for_status()
    return possess(ptr)


def sched_db_get_by_hmm_id(hmm_id: int) -> sched_db:
    ptr = new_db()
    rc = RC(lib.sched_db_get_by_hmm_id(ptr, hmm_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_db_get_all() -> List[sched_db]:
    dbs: List[sched_db] = []
    ptr = new_db()
    rc = RC(lib.sched_db_get_all(lib.append_db, ptr, ffi.new_handle(dbs)))
    rc.raise_for_status()
    return dbs


@ffi.def_extern()
def append_db(ptr, arg):
    sched_dbs = ffi.from_handle(arg)
    sched_dbs.append(possess(ptr))
