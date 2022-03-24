from typing import List

from fastapi import APIRouter, Path
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.errors import ErrorResponse
from deciphon_api.models.db import DB

router = APIRouter()


@router.get(
    "/dbs/{db_id}",
    summary="get database",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="dbs:get-database",
)
def get_database(db_id: int = Path(..., gt=0)):
    return DB.get_by_id(db_id)


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
    return DB.get_list()


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
    db = DB.get_by_id(db_id)
    media_type = "application/octet-stream"
    return FileResponse(db.filename, media_type=media_type, filename=db.filename)


class DBFileName(BaseModel):
    filename: str


@router.post(
    "/dbs/",
    summary="upload a new database",
    response_model=DB,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="dbs:upload-database",
)
def upload_database(db: DBFileName):
    return DB.add(db.filename)
