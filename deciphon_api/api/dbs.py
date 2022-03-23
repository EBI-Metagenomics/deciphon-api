from typing import List

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api._types import ErrorResponse
from deciphon_api.csched import ffi, lib
from deciphon_api.db import DB
from deciphon_api.exception import EINVALException, create_exception
from deciphon_api.rc import RC

router = APIRouter()


@router.get(
    "/dbs/{db_id}",
    summary="get database",
    response_model=List[DB],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="dbs:get-database",
)
def get_database(db_id: int):
    cdb = ffi.new("struct sched_db *")
    cdb[0].id = db_id

    rc = RC(lib.sched_db_get(cdb))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise EINVALException(HTTP_404_NOT_FOUND, "database not found")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return [DB.from_cdata(cdb)]


@router.get(
    "/dbs",
    summary="get database list",
    response_model=List[DB],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="dbs:get-database-list",
)
def get_database_list():
    ptr = ffi.new("struct sched_db *")

    dbs: List[DB] = []
    rc = RC(lib.sched_db_get_all(lib.append_db, ptr, ffi.new_handle(dbs)))
    assert rc != RC.END

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return dbs


@router.get(
    "/dbs/{db_id}/download",
    summary="download database",
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="dbs:download-database",
)
def download_database(db_id: int):
    ptr = ffi.new("struct sched_db *")

    rc = RC(lib.sched_db_get_by_id(ptr, db_id))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise EINVALException(HTTP_404_NOT_FOUND, "database not found")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    db = DB.from_cdata(ptr[0])
    media_type = "application/octet-stream"
    return FileResponse(db.filename, media_type=media_type, filename=db.filename)


class DBFileName(BaseModel):
    filename: str


@router.post(
    "/dbs/",
    summary="add a new database",
    description="the file must reside at the sched working directory",
    response_model=DB,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="dbs:add-database",
)
def add_database(db: DBFileName):
    return DB.add(db.filename)
