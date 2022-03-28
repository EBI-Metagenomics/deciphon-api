from __future__ import annotations

import os
import tempfile
from typing import List

from pydantic import BaseModel

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import InternalError
from deciphon_api.rc import RC

__all__ = ["SchedHealth"]


class SchedHealth(BaseModel):
    num_errors: int = 0
    errors: List[str] = []

    def check(self):
        file = tempfile.SpooledTemporaryFile(mode="r+")
        fp = lib.fdopen(os.dup(file.fileno()), b"r+")

        p_health = ffi.new("struct sched_health *")
        c_health = p_health[0]
        c_health.fp = fp
        c_health.num_errors = 0

        rc = RC(lib.sched_health_check(p_health))

        if rc != RC.OK:
            raise InternalError(rc)

        file.flush()

        self.num_errors = int(c_health.num_errors)
        file.seek(0)
        for row in file:
            self.errors.append(row.strip())

        file.close()
