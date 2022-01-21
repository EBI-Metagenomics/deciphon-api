from fastapi import Query
from pydantic import BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .rc import Code, RC, ReturnData


class DB(BaseModel):
    id: int = 0
    xxh64: int = 0
    filename: str = ""

    @classmethod
    def from_cdata(cls, cdb):
        return cls(
            id=int(cdb[0].id),
            xxh64=int(cdb[0].xxh64),
            filename=ffi.string(cdb[0].filename).decode(),
        )


@app.get(
    "/dbs/{db_id}",
    summary="get database",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_db(db_id: int):
    cdb = ffi.new("struct sched_db *")
    cdb[0].id = db_id

    rc = RC(lib.sched_db_get(cdb))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "database not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return DB.from_cdata(cdb)


def db_exists(filename: str):
    cdb = ffi.new("struct sched_db *")
    cdb[0].filename = filename.encode()
    rc = RC(lib.sched_db_get(cdb))

    if rc == RC.DONE:
        return True

    if rc == RC.NOTFOUND:
        return False

    raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])


@app.post(
    "/dbs",
    summary="add a new database",
    description="the file must reside at the sched working directory",
    response_model=DB,
    status_code=HTTP_201_CREATED,
    responses={HTTP_409_CONFLICT: {"model": ReturnData}},
)
def post_db(
    filename: str = Query(..., example="pfam24.dcp", description="database filename")
):
    if db_exists(filename):
        raise DCPException(
            HTTP_409_CONFLICT,
            Code.EINVAL,
            "database with same filename already exists",
        )

    cdb = ffi.new("struct sched_db *")
    cdb[0].filename = filename.encode()
    rc = RC(lib.sched_db_add(cdb, filename.encode()))

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return DB.from_cdata(cdb)
