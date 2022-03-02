from fastapi import Query
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .db import DB
from .exception import DCPException
from .rc import RC, StrRC
from .response import ErrorResponse


@app.post(
    "/dbs",
    summary="add a new database",
    description="the file must reside at the sched working directory",
    response_model=DB,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppost_dbs(
    filename: str = Query(..., example="pfam24.dcp", description="database filename")
):
    if DB.exists(filename):
        raise DCPException(
            HTTP_409_CONFLICT,
            StrRC.EINVAL,
            "database already exists",
        )

    cdb = ffi.new("struct sched_db *")
    cdb[0].filename = filename.encode()
    rc = RC(lib.sched_db_add(cdb, filename.encode()))

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return DB.from_cdata(cdb)
