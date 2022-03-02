from typing import List

from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from ._app import app
from .csched import ffi, lib
from .db import DB
from .exception import DCPException
from .rc import RC, StrRC
from .response import ErrorResponse


@app.get(
    "/dbs",
    summary="get database list",
    response_model=List[DB],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_dbs():
    cdb = ffi.new("struct sched_db *")
    cdb[0].id = 0

    dbs: List[DB] = []
    rc = RC(lib.sched_db_get_all(lib.append_db_callback, cdb, ffi.new_handle(dbs)))

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return dbs
