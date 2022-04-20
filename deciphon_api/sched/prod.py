from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.rc import RC

__all__ = ["sched_prod", "sched_prod_new", "sched_prod_get_by_id", "sched_prod_get_all"]


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


def possess(ptr):
    c = ptr[0]
    return sched_prod(
        int(c.id),
        int(c.scan_id),
        int(c.seq_id),
        ffi.string(c.profile_name).decode(),
        ffi.string(c.abc_name).decode(),
        float(c.alt_loglik),
        float(c.null_loglik),
        ffi.string(c.profile_typeid).decode(),
        ffi.string(c.version).decode(),
        ffi.string(c.match).decode(),
        ptr,
    )


def sched_prod_new():
    ptr = ffi.new("struct sched_prod *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)


def sched_prod_get_by_id(prod_id: int) -> sched_prod:
    ptr = sched_prod_new()
    rc = RC(lib.sched_prod_get_by_id(ptr, prod_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_prod_get_all() -> List[sched_prod]:
    prods: List[sched_prod] = []
    ptr = sched_prod_new()
    rc = RC(lib.sched_prod_get_all(lib.append_prod, ptr, ffi.new_handle(prods)))
    rc.raise_for_status()
    return prods


@ffi.def_extern()
def append_prod(ptr, arg):
    sched_prods = ffi.from_handle(arg)
    sched_prods.append(possess(ptr))
