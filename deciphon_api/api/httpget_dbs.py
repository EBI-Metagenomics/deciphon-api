from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from .._types import ErrorResponse
from ..csched import ffi, lib
from ..db import DB
from ..exception import create_exception
from ..rc import RC

router = APIRouter()


@router.get(
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
    assert rc != RC.END

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return dbs
