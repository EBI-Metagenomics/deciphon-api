from __future__ import annotations

import tempfile
from typing import List

from pydantic import BaseModel

from deciphon_api.sched.sched import sched_health_check

__all__ = ["SchedHealth"]


class SchedHealth(BaseModel):
    num_errors: int = 0
    errors: List[str] = []

    def check(self):
        with tempfile.SpooledTemporaryFile(mode="r+") as file:
            return sched_health_check(file)
