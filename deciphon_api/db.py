from pydantic import BaseModel, Field
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from .csched import ffi, lib
from .exception import DCPException
from .rc import RC, Code

__all__ = ["DB"]


class DB(BaseModel):
    id: int = Field(..., gt=0)
    xxh64: int = Field(..., title="XXH64 file hash")
    filename: str = Field(...)

    @classmethod
    def from_cdata(cls, cdb):
        return cls(
            id=int(cdb[0].id),
            xxh64=int(cdb[0].xxh64),
            filename=ffi.string(cdb[0].filename).decode(),
        )

    @staticmethod
    def exists(filename: str):
        cdb = ffi.new("struct sched_db *")
        cdb[0].filename = filename.encode()
        rc = RC(lib.sched_db_get(cdb))

        if rc == RC.OK:
            return True

        if rc == RC.NOTFOUND:
            return False

        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])


@ffi.def_extern()
def append_db_callback(cdb, arg):
    dbs = ffi.from_handle(arg)
    dbs.append(DB.from_cdata(cdb))
