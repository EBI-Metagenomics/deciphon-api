from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.rc import RC

__all__ = [
    "sched_seq",
    "sched_seq_new",
    "sched_seq_get_by_id",
    "sched_seq_get_all",
    "sched_seq_scan_next",
]


def string(cdata) -> str:
    return ffi.string(cdata).decode()


@dataclass
class sched_seq:
    id: int
    scan_id: int
    name: str
    data: str
    ptr: Any

    def refresh(self):
        c = self.ptr[0]

        self.id = int(c.id)
        self.scan_id = int(c.scan_id)

        self.name = string(c.name)
        self.data = string(c.data)


def possess(ptr):
    c = ptr[0]
    return sched_seq(
        int(c.id),
        int(c.scan_id),
        string(c.name),
        string(c.data),
        ptr,
    )


def sched_seq_new(seq_id: int, scan_id: int) -> sched_seq:
    ptr = ffi.new("struct sched_seq *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    lib.sched_seq_init(ptr, seq_id, scan_id, "".encode(), "".encode())
    return possess(ptr)


def new_seq():
    return sched_seq_new(0, 0).ptr


def sched_seq_get_by_id(seq_id: int) -> sched_seq:
    ptr = new_seq()
    rc = RC(lib.sched_seq_get_by_id(ptr, seq_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_seq_get_all() -> List[sched_seq]:
    seqs: List[sched_seq] = []
    ptr = new_seq()
    rc = RC(lib.sched_seq_get_all(lib.append_seq, ptr, ffi.new_handle(seqs)))
    rc.raise_for_status()
    return seqs


def sched_seq_scan_next(seq: sched_seq):
    rc = RC(lib.sched_seq_scan_next(seq.ptr))
    rc.raise_for_status()
    seq.refresh()


@ffi.def_extern()
def append_seq(ptr, arg):
    sched_seqs = ffi.from_handle(arg)
    sched_seqs.append(possess(ptr))
