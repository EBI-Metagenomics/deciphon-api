from dataclasses import dataclass
from typing import Any, List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.prod import sched_prod, sched_prod_new
from deciphon_api.sched.rc import RC
from deciphon_api.sched.seq import sched_seq, sched_seq_new

__all__ = [
    "sched_scan",
    "sched_scan_get_by_id",
    "sched_scan_get_by_job_id",
    "sched_scan_get_seqs",
    "sched_scan_get_prods",
    "sched_scan_get_all",
    "sched_scan_new",
    "sched_scan_add_seq",
]


@dataclass
class sched_scan:
    id: int
    db_id: int

    multi_hits: bool
    hmmer3_compat: bool

    job_id: int

    ptr: Any

    def refresh(self):
        c = self.ptr[0]

        self.id = int(c.id)
        self.db_id = int(c.db_id)

        self.multi_hits = bool(c.multi_hits)
        self.hmmer3_compat = bool(c.hmmer3_compat)

        self.job_id = int(c.job_id)


def possess(ptr):
    c = ptr[0]
    return sched_scan(
        int(c.id),
        int(c.db_id),
        bool(c.multi_hits),
        bool(c.hmmer3_compat),
        int(c.job_id),
        ptr,
    )


def new_scan():
    ptr = ffi.new("struct sched_scan *")
    if ptr == ffi.NULL:
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)
    return ptr


def sched_scan_add_seq(name: str, data: str):
    lib.sched_scan_add_seq(name.encode(), data.encode())


def sched_scan_new(db_id: int, multi_hits: bool, hmmer3_compat: bool) -> sched_scan:
    ptr = new_scan()
    lib.sched_scan_init(ptr, db_id, multi_hits, hmmer3_compat)
    return possess(ptr)


def sched_scan_get_by_id(scan_id: int) -> sched_scan:
    ptr = new_scan()
    rc = RC(lib.sched_scan_get_by_id(ptr, scan_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_scan_get_by_job_id(job_id: int) -> sched_scan:
    ptr = new_scan()
    rc = RC(lib.sched_scan_get_by_job_id(ptr, job_id))
    rc.raise_for_status()
    return possess(ptr)


def sched_scan_get_seqs(scan_id: int):
    seqs: List[sched_seq] = []
    ptr = sched_seq_new(0, scan_id).ptr
    rc = RC(lib.sched_scan_get_seqs(scan_id, lib.append_seq, ptr, ffi.new_handle(seqs)))
    rc.raise_for_status()
    return seqs


def sched_scan_get_prods(scan_id: int) -> List[sched_prod]:
    prods: List[sched_prod] = []
    ptr = sched_prod_new().ptr
    hdl = ffi.new_handle(prods)
    rc = RC(lib.sched_scan_get_prods(scan_id, lib.append_prod, ptr, hdl))
    rc.raise_for_status()
    return prods


def sched_scan_get_all() -> List[sched_scan]:
    scans: List[sched_scan] = []
    ptr = new_scan()
    rc = RC(lib.sched_scan_get_all(lib.append_scan, ptr, ffi.new_handle(scans)))
    rc.raise_for_status()
    return scans


@ffi.def_extern()
def append_scan(ptr, arg):
    sched_scans = ffi.from_handle(arg)
    sched_scans.append(possess(ptr))
