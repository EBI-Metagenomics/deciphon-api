from __future__ import annotations

from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field

from deciphon_api.core.errors import InvalidTypeError
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.hmm import (
    sched_hmm,
    sched_hmm_get_all,
    sched_hmm_get_by_filename,
    sched_hmm_get_by_id,
    sched_hmm_get_by_job_id,
    sched_hmm_get_by_xxh3,
    sched_hmm_new,
    sched_hmm_remove,
)
from deciphon_api.sched.job import sched_job_submit
from deciphon_api.sched.rc import RC

__all__ = ["HMM", "HMMIDType"]


class HMMIDType(str, Enum):
    HMM_ID = "hmm_id"
    XXH3 = "xxh3"
    FILENAME = "filename"
    JOB_ID = "job_id"


class HMM(BaseModel):
    id: int = Field(..., gt=0)
    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = ""
    job_id: int = Field(..., gt=0)

    @classmethod
    def from_sched_hmm(cls, hmm: sched_hmm):
        return cls(
            id=hmm.id,
            xxh3=hmm.xxh3,
            filename=hmm.filename,
            job_id=hmm.job_id,
        )

    @staticmethod
    def submit(filename: str) -> HMM:
        hmm = sched_hmm_new(filename)
        sched_job_submit(hmm)
        return HMM.from_sched_hmm(hmm)

    @staticmethod
    def get(id: Union[int, str], id_type: HMMIDType) -> HMM:
        # if id_type == HMMIDType.FILENAME and not isinstance(id, str):
        #     raise InvalidTypeError("Expected string")
        # elif id_type != HMMIDType.FILENAME and not isinstance(id, int):
        #     raise InvalidTypeError("Expected integer")

        if id_type == HMMIDType.HMM_ID:
            if not isinstance(id, int):
                raise InvalidTypeError("integer")
            return HMM.from_sched_hmm(sched_hmm_get_by_id(id))

        if id_type == HMMIDType.XXH3:
            if not isinstance(id, int):
                raise InvalidTypeError("integer")
            return HMM.from_sched_hmm(sched_hmm_get_by_xxh3(id))

        if id_type == HMMIDType.FILENAME:
            if not isinstance(id, str):
                raise InvalidTypeError("string")
            return HMM.from_sched_hmm(sched_hmm_get_by_filename(id))

        if id_type == HMMIDType.JOB_ID:
            if not isinstance(id, int):
                raise InvalidTypeError("integer")
            return HMM.from_sched_hmm(sched_hmm_get_by_job_id(id))

    @staticmethod
    def exists_by_id(hmm_id: int) -> bool:
        try:
            HMM.get(hmm_id, HMMIDType.HMM_ID)
        except SchedError as error:
            if error.rc == RC.SCHED_HMM_NOT_FOUND:
                return False
            raise
        return True

    @staticmethod
    def exists_by_filename(filename: str) -> bool:
        try:
            HMM.get(filename, HMMIDType.FILENAME)
        except SchedError as error:
            if error.rc == RC.SCHED_HMM_NOT_FOUND:
                return False
            raise
        return True

    @staticmethod
    def get_list() -> List[HMM]:
        return [HMM.from_sched_hmm(hmm) for hmm in sched_hmm_get_all()]

    @staticmethod
    def remove(hmm_id: int):
        sched_hmm_remove(hmm_id)
