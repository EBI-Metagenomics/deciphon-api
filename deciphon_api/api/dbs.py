import shutil
from typing import List, Union

from fastapi import APIRouter, Depends, File, Path, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import UnauthorizedError
from deciphon_api.models.db import DB, DBIDType

router = APIRouter()


mime = "application/octet-stream"


@router.get(
    "/dbs/{id}",
    summary="get database",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-database",
)
def get_database(
    id: Union[int, str] = Path(...), id_type: DBIDType = Query(DBIDType.DB_ID.value)
):
    return DB.get(id, id_type)


@router.get(
    "/dbs",
    summary="get database list",
    response_model=List[DB],
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-database-list",
)
def get_database_list():
    return DB.get_list()


@router.get(
    "/dbs/{db_id}/download",
    summary="download database",
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:download-database",
)
def download_database(db_id: int = Path(..., gt=0)):
    db = DB.get(db_id, DBIDType.DB_ID)
    return FileResponse(db.filename, media_type=mime, filename=db.filename)


@router.post(
    "/dbs/",
    summary="upload a new database",
    response_model=DB,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="dbs:upload-database",
)
def upload_database(
    db_file: UploadFile = File(..., content_type=mime, description="deciphon database"),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    with open(db_file.filename, "wb") as dst:
        shutil.copyfileobj(db_file.file, dst)

    return DB.add(db_file.filename)


@router.delete(
    "/dbs/{db_id}",
    summary="remove db",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:remove-db",
)
def remove_db(
    db_id: int = Path(..., gt=0), authenticated: bool = Depends(auth_request)
):
    if not authenticated:
        raise UnauthorizedError()

    DB.remove(db_id)
    return JSONResponse({})
