import os
from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError, SchedWrapperError
from deciphon_api.sched.rc import RC

__all__ = [
    "sched_prod",
    "sched_prod_new",
    "sched_prod_get_by_id",
    "sched_prod_get_all",
    "sched_prod_add_file",
]


@dataclass
class sched_prod:
    id: int

    scan_id: int
    seq_id: int

    profile_name: str
    abc_name: str

    alt_loglik: float
    null_loglik: float

    profile_typeid: str
    version: str

    match: str

    ptr: Any


def string(cdata) -> str:
    return ffi.string(cdata).decode()


def possess(ptr):
    c = ptr[0]
    return sched_prod(
        int(c.id),
        int(c.scan_id),
        int(c.seq_id),
        string(c.profile_name),
        string(c.abc_name),
        float(c.alt_loglik),
        float(c.null_loglik),
        string(c.profile_typeid),
        string(c.version),
        string(c.match),
        ptr,
    )


def new_prod():
    ptr = ffi.new("struct sched_prod *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    return ptr


def sched_prod_new() -> sched_prod:
    return possess(new_prod())


def sched_prod_get_by_id(prod_id: int) -> sched_prod:
    ptr = new_prod()
    rc = RC(lib.sched_prod_get_by_id(ptr, prod_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_prod_get_all() -> List[sched_prod]:
    prods: List[sched_prod] = []
    ptr = new_prod()
    rc = RC(lib.sched_prod_get_all(lib.append_prod, ptr, ffi.new_handle(prods)))
    rc.raise_for_status()
    return prods


def sched_prod_add_file(file):
    fd = os.dup(file.fileno())
    if fd == -1:
        raise SchedWrapperError(RC.SCHED_FAIL_OPEN_FILE)

    fp = lib.fdopen(fd, b"r+")
    if fp == ffi.NULL:
        raise SchedWrapperError(RC.SCHED_FAIL_OPEN_FILE)

    rc = RC(lib.sched_prod_add_file(fp))
    lib.fclose(fp)
    rc.raise_for_status()


@ffi.def_extern()
def append_prod(ptr, arg):
    sched_prods = ffi.from_handle(arg)
    sched_prods.append(possess(ptr))
