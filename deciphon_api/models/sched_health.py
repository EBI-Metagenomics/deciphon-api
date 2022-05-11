from __future__ import annotations

import tempfile
from typing import List

from deciphon_sched.sched import sched_health_check
from pydantic import BaseModel

__all__ = ["SchedHealth"]


class SchedHealth(BaseModel):
    num_errors: int = 0
    errors: List[str] = []

    def check(self):
        with tempfile.SpooledTemporaryFile(mode="r+") as file:
            return sched_health_check(file)
