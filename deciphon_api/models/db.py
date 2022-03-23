from pathlib import Path

from pydantic import BaseModel, Field
from starlette.status import (
    HTTP_409_CONFLICT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import EINVALException, create_exception
from deciphon_api.rc import RC

__all__ = ["DB"]


class DB(BaseModel):
    id: int = Field(..., gt=0)
    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = ""
    hmm_id: int = Field(..., gt=0)

    @classmethod
    def from_cdata(cls, cdb):
        return cls(
            id=int(cdb.id),
            xxh3=int(cdb.xxh3),
            filename=ffi.string(cdb.filename).decode(),
            hmm_id=int(cdb.hmm_id),
        )

    @staticmethod
    def add(filename: str):
        if DB.exists_by_filename(filename):
            raise EINVALException(
                HTTP_409_CONFLICT,
                "database already exists",
            )

        if not Path(filename).exists():
            raise EINVALException(HTTP_412_PRECONDITION_FAILED, "file not found")

        ptr = ffi.new("struct sched_db *")
        rc = RC(lib.sched_db_add(ptr, filename.encode()))

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return DB.from_cdata(ptr[0])

    @staticmethod
    def exists_by_id(db_id: int) -> bool:
        ptr = ffi.new("struct sched_db *")

        rc = RC(lib.sched_db_get_by_id(ptr, db_id))
        assert rc != RC.END

        if rc == RC.OK:
            return True

        if rc == RC.NOTFOUND:
            return False

        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    @staticmethod
    def exists_by_filename(filename: str) -> bool:
        ptr = ffi.new("struct sched_db *")

        rc = RC(lib.sched_db_get_by_filename(ptr, filename.encode()))
        assert rc != RC.END

        if rc == RC.OK:
            return True

        if rc == RC.NOTFOUND:
            return False

        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)


@ffi.def_extern()
def append_db(ptr, arg):
    dbs = ffi.from_handle(arg)
    dbs.append(DB.from_cdata(ptr[0]))
