from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .db import DB
from .exception import DCPException
from .rc import RC, StrRC
from ._types import ErrorResponse


@app.get(
    "/dbs/{db_id}",
    summary="get database",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_dbs_xxx(db_id: int):
    cdb = ffi.new("struct sched_db *")
    cdb[0].id = db_id

    rc = RC(lib.sched_db_get(cdb))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "database not found")

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return DB.from_cdata(cdb)
