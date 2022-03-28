from __future__ import annotations

from pathlib import Path
from typing import Any, List, Tuple

from pydantic import BaseModel, Field

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import ConditionError, InternalError, NotFoundError
from deciphon_api.rc import RC

__all__ = ["HMM"]


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
    def submit(filename: str):
        if not Path(filename).exists():
            raise NotFoundError("file")

        hmm_ptr = ffi.new("struct sched_hmm *")
        lib.sched_hmm_init(hmm_ptr)
        rc = RC(lib.sched_hmm_set_file(hmm_ptr, filename.encode()))
        if rc == RC.EINVAL:
            raise ConditionError("invalid hmm file name")

        job_ptr = ffi.new("struct sched_job *")
        lib.sched_job_init(job_ptr, lib.SCHED_HMM)
        rc = RC(lib.sched_job_submit(job_ptr, hmm_ptr))
        assert rc != RC.END
        assert rc != RC.NOTFOUND

        if rc != RC.OK:
            raise InternalError(rc)

        return HMM.from_cdata(hmm_ptr[0])

    @staticmethod
    def get_by_id(hmm_id: int) -> HMM:
        return resolve_get_hmm(*get_by_id(hmm_id))

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


def get_by_id(hmm_id: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_hmm *")

    rc = RC(lib.sched_hmm_get_by_id(ptr, hmm_id))
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
