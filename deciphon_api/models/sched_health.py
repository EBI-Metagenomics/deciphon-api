from __future__ import annotations

import os
import tempfile
from typing import List

from pydantic import BaseModel

from deciphon_api.core.errors import InternalError
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

__all__ = ["SchedHealth"]


class SchedHealth(BaseModel):
    num_errors: int = 0
    errors: List[str] = []

    def check(self):
        file = tempfile.SpooledTemporaryFile(mode="r+")
        fd = os.dup(file.fileno())
        if fd == -1:
            raise InternalError(RC.EFAIL, "Failed to duplicate file descriptor.")

        fp = lib.fdopen(fd, b"r+")
        if fp == ffi.NULL:
            raise InternalError(RC.EFAIL, "Failed to fdopen a file descriptor.")

        p_health = ffi.new("struct sched_health *")
        c_health = p_health[0]
        c_health.fp = fp
        c_health.num_errors = 0

        try:
            rc = RC(lib.sched_health_check(p_health))
            if rc != RC.OK:
                raise InternalError(rc)
        finally:
            lib.fclose(fp)

        file.flush()
        file.seek(0)

        self.num_errors = int(c_health.num_errors)
        for row in file:
            self.errors.append(row.strip())

        file.close()
