from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, List, Tuple, Union

from pydantic import BaseModel, Field

from deciphon_api.core.errors import (
    ConditionError,
    ConstraintError,
    InternalError,
    InvalidTypeError,
    NotFoundError,
)
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

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
    def from_cdata(cls, chmm):
        return cls(
            id=int(chmm.id),
            xxh3=int(chmm.xxh3),
            filename=ffi.string(chmm.filename).decode(),
            job_id=int(chmm.job_id),
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

        return HMM.from_cdata(p_hmm[0])

    @staticmethod
    def get(id: Union[int, str], id_type: HMMIDType) -> HMM:
        if id_type == HMMIDType.FILENAME and not isinstance(id, str):
            raise InvalidTypeError("Expected string")
        elif id_type != HMMIDType.FILENAME and not isinstance(id, int):
            raise InvalidTypeError("Expected integer")

        if id_type == HMMIDType.HMM_ID:
            assert isinstance(id, int)
            return resolve_get_hmm(*get_by_id(id))

        if id_type == HMMIDType.XXH3:
            assert isinstance(id, int)
            return resolve_get_hmm(*get_by_xxh3(id))

        if id_type == HMMIDType.FILENAME:
            assert isinstance(id, str)
            return resolve_get_hmm(*get_by_filename(id))

        if id_type == HMMIDType.JOB_ID:
            assert isinstance(id, int)
            return resolve_get_hmm(*get_by_job_id(id))

    @staticmethod
    def get_by_id(hmm_id: int) -> HMM:
        return resolve_get_hmm(*get_by_id(hmm_id))

    @staticmethod
    def get_by_job_id(job_id: int) -> HMM:
        return resolve_get_hmm(*get_by_job_id(job_id))

    @staticmethod
    def get_by_xxh3(xxh3: int) -> HMM:
        return resolve_get_hmm(*get_by_xxh3(xxh3))

    @staticmethod
    def get_by_filename(filename: str) -> HMM:
        return resolve_get_hmm(*get_by_filename(filename))

    @staticmethod
    def exists_by_id(hmm_id: int) -> bool:
        try:
            HMM.get_by_id(hmm_id)
        except NotFoundError:
            return False
        return True

    @staticmethod
    def exists_by_filename(filename: str) -> bool:
        try:
            HMM.get_by_filename(filename)
        except NotFoundError:
            return False
        return True

    @staticmethod
    def get_list() -> List[HMM]:
        ptr = ffi.new("struct sched_hmm *")

        hmms: List[HMM] = []
        rc = RC(lib.sched_hmm_get_all(lib.append_hmm, ptr, ffi.new_handle(hmms)))
        assert rc != RC.END

        if rc != RC.OK:
            raise InternalError(rc)

        return hmms

    @staticmethod
    def remove(hmm_id: int):
        rc = RC(lib.sched_hmm_remove(hmm_id))

        if rc == RC.NOTFOUND:
            raise NotFoundError("hmm")

        if rc == RC.ECONSTRAINT:
            raise ConstraintError("can't remove referenced hmm")

        if rc != RC.OK:
            raise InternalError(rc)


def get_by_id(hmm_id: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_hmm *")

    rc = RC(lib.sched_hmm_get_by_id(ptr, hmm_id))
    assert rc != RC.END

    return (ptr, rc)


def get_by_job_id(job_id: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_hmm *")

    rc = RC(lib.sched_hmm_get_by_job_id(ptr, job_id))
    assert rc != RC.END

    return (ptr, rc)


def get_by_xxh3(xxh3: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_hmm *")

    rc = RC(lib.sched_hmm_get_by_xxh3(ptr, xxh3))
    assert rc != RC.END

    return (ptr, rc)


def get_by_filename(filename: str) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_hmm *")

    rc = RC(lib.sched_hmm_get_by_filename(ptr, filename.encode()))
    assert rc != RC.END

    return (ptr, rc)


def resolve_get_hmm(ptr: Any, rc: RC) -> HMM:
    if rc == RC.OK:
        return HMM.from_cdata(ptr[0])

    if rc == RC.NOTFOUND:
        raise NotFoundError("hmm")

    raise InternalError(rc)


@ffi.def_extern()
def append_hmm(ptr, arg):
    hmms = ffi.from_handle(arg)
    hmms.append(HMM.from_cdata(ptr[0]))
