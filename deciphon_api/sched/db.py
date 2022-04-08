from dataclasses import dataclass
from typing import Any, List, Tuple

from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib


@dataclass
class sched_db:
    id: int
    xxh3: int
    filename: str
    hmm_id: int
    ptr: Any


def ptr_to_db(ptr):
    c = ptr[0]
    return sched_db(
        int(c.id), int(c.xxh3), ffi.string(c.filename).decode(), int(c.hmm_id), ptr
    )


def sched_db_new() -> sched_db:
    ptr = ffi.new("struct sched_db *")
    lib.sched_db_init(ptr)
    return ptr_to_db(ptr)


def sched_db_add(filename: str) -> Tuple[RC, sched_db]:
    ptr = ffi.new("struct sched_db *")
    rc = RC(lib.sched_db_add(ptr, filename.encode()))
    return rc, ptr_to_db(ptr)


def sched_db_remove(db_id: int) -> RC:
    return RC(lib.sched_db_remove(db_id))


def sched_db_get_by_id(db_id: int) -> Tuple[RC, Any]:
    ptr = sched_db_new()
    return RC(lib.sched_db_get_by_id(ptr, db_id)), ptr


def sched_db_get_by_filename(filename: str) -> Tuple[RC, Any]:
    ptr = sched_db_new()
    return RC(lib.sched_db_get_by_filename(ptr, filename.encode())), ptr


def sched_db_get_all(sched_dbs: List[sched_db]) -> RC:
    ptr = sched_db_new()
    return RC(lib.sched_db_get_all(lib.append_db, ptr, ffi.new_handle(sched_dbs)))


# @ffi.def_extern()
def append_db(ptr, arg):
    sched_dbs = ffi.from_handle(arg)
    sched_dbs.append(ptr_to_db(ptr))
