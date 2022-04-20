import os
from typing import List

from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.error import SchedError, SchedWrapperError
from deciphon_api.sched.rc import RC

__all__ = ["sched_init", "sched_cleanup", "sched_wipe", "sched_health_check"]


def sched_init(file_name: str):
    rc = RC(lib.sched_init(file_name.encode()))
    rc.raise_for_status()


def sched_cleanup():
    rc = RC(lib.sched_cleanup())
    rc.raise_for_status()


def sched_health_check(file) -> List[str]:
    fd = os.dup(file.fileno())
    if fd == -1:
        raise SchedWrapperError(RC.SCHED_FAIL_OPEN_FILE)

    fp = lib.fdopen(fd, b"r+")
    if fp == ffi.NULL:
        raise SchedWrapperError(RC.SCHED_FAIL_OPEN_FILE)

    ptr = ffi.new("struct sched_health *")
    if ptr == ffi.NULL:
        lib.fclose(fp)
        raise SchedError(RC.SCHED_NOT_ENOUGH_MEMORY)

    ptr[0].fp = fp
    ptr[0].num_errors = 0
    rc = RC(lib.sched_health_check(ptr))

    lib.fclose(fp)
    rc.raise_for_status()

    file.flush()
    file.seek(0)

    errors: List[str] = []
    for row in file:
        errors.append(row.strip())

    return errors


def sched_wipe():
    rc = RC(lib.sched_wipe())
    rc.raise_for_status()
