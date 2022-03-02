from fastapi import Query
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from ._types import ErrorResponse
from .csched import ffi, lib
from .db import DB
from .exception import EINVALException, create_exception
from .rc import RC


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
        raise EINVALException(
            HTTP_409_CONFLICT,
            "database already exists",
        )

    cdb = ffi.new("struct sched_db *")
    cdb[0].filename = filename.encode()
    rc = RC(lib.sched_db_add(cdb, filename.encode()))

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return DB.from_cdata(cdb)
