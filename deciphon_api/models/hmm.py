from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, Field

from deciphon_api.core.errors import (
    ConditionError,
    InternalError,
    InvalidTypeError,
    NotFoundError,
)
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.hmm import (
    possess,
    sched_hmm,
    sched_hmm_get_all,
    sched_hmm_get_by_filename,
    sched_hmm_get_by_id,
    sched_hmm_get_by_job_id,
    sched_hmm_get_by_xxh3,
    sched_hmm_remove,
)

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
        if not Path(filename).exists():
            raise NotFoundError("file")

        p_hmm = ffi.new("struct sched_hmm *")
        lib.sched_hmm_init(p_hmm)

        rc = RC(lib.sched_hmm_set_file(p_hmm, filename.encode()))
        if rc == RC.EINVAL:
            raise ConditionError("invalid hmm file name")

        job_ptr = ffi.new("struct sched_job *")
        lib.sched_job_init(job_ptr, lib.SCHED_HMM)
        rc = RC(lib.sched_job_submit(job_ptr, p_hmm))
        assert rc != RC.END
        assert rc != RC.NOTFOUND

        if rc != RC.OK:
            raise InternalError(rc)

        return HMM.from_sched_hmm(possess(p_hmm))

    @staticmethod
    def get(id: Union[int, str], id_type: HMMIDType) -> HMM:
        if id_type == HMMIDType.FILENAME and not isinstance(id, str):
            raise InvalidTypeError("Expected string")
        elif id_type != HMMIDType.FILENAME and not isinstance(id, int):
            raise InvalidTypeError("Expected integer")

        if id_type == HMMIDType.HMM_ID:
            assert isinstance(id, int)
            return HMM.from_sched_hmm(sched_hmm_get_by_id(id))

        if id_type == HMMIDType.XXH3:
            assert isinstance(id, int)
            return HMM.from_sched_hmm(sched_hmm_get_by_xxh3(id))

        if id_type == HMMIDType.FILENAME:
            assert isinstance(id, str)
            return HMM.from_sched_hmm(sched_hmm_get_by_filename(id))

        if id_type == HMMIDType.JOB_ID:
            assert isinstance(id, int)
            return HMM.from_sched_hmm(sched_hmm_get_by_job_id(id))

    @staticmethod
    def exists_by_id(hmm_id: int) -> bool:
        try:
            HMM.get(hmm_id, HMMIDType.HMM_ID)
        except NotFoundError:
            return False
        return True

    @staticmethod
    def exists_by_filename(filename: str) -> bool:
        try:
            HMM.get(filename, HMMIDType.FILENAME)
        except NotFoundError:
            return False
        return True

    @staticmethod
    def get_list() -> List[HMM]:
        return [HMM.from_sched_hmm(hmm) for hmm in sched_hmm_get_all()]

    @staticmethod
    def remove(hmm_id: int):
        sched_hmm_remove(hmm_id)
