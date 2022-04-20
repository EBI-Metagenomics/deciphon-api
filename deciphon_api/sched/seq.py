from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.rc import RC


@dataclass
class sched_seq:
    id: int
    scan_id: int
    name: str
    data: str
    ptr: Any


def possess(ptr):
    c = ptr[0]
    return sched_seq(
        int(c.id),
        int(c.scan_id),
        ffi.string(c.name).decode(),
        ffi.string(c.data).decode(),
        ptr,
    )


def sched_seq_new():
    ptr = ffi.new("struct sched_seq *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)


def sched_seq_get_by_id(seq_id: int) -> sched_seq:
    ptr = sched_seq_new()
    rc = RC(lib.sched_seq_get_by_id(ptr, seq_id))
    if RC.is_error(rc):
        raise SchedError(rc)
    return possess(ptr)


def sched_seq_get_all() -> List[sched_seq]:
    seqs: List[sched_seq] = []
    ptr = sched_seq_new()
    rc = RC(lib.sched_seq_get_all(lib.append_seq, ptr, ffi.new_handle(seqs)))
    if RC.is_error(rc):
        raise SchedError(rc)
    return seqs


@ffi.def_extern()
def append_seq(ptr, arg):
    sched_seqs = ffi.from_handle(arg)
    sched_seqs.append(possess(ptr))
