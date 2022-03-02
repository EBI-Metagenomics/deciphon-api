from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from ._types import ErrorResponse
from .csched import ffi, lib
from .db import DB
from .exception import create_exception
from .rc import RC


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
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return DB.from_cdata(cdb)
