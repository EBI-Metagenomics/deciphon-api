from pathlib import Path
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_409_CONFLICT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .._types import ErrorResponse
from ..csched import ffi, lib
from ..db import DB
from ..exception import EINVALException, create_exception
from ..rc import RC


class DBFileName(BaseModel):
    filename: str = "minifam.dcp"


router = APIRouter()


@router.post(
    "/dbs/",
    summary="add a new database",
    description="the file must reside at the sched working directory",
    response_model=List[DB],
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppost_dbs(db: DBFileName):
    filepath = Path(db.filename)
    if not filepath.exists():
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "file not found")

    if DB.exists(db.filename):
        raise EINVALException(
            HTTP_409_CONFLICT,
            "database already exists",
        )

    print(db.filename)
    print(db.filename)
    cdb = ffi.new("struct sched_db *")
    cdb[0].filename = db.filename.encode()
    rc = RC(lib.sched_db_add(cdb, db.filename.encode()))

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return [DB.from_cdata(cdb)]