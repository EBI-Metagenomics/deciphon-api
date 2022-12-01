import ctypes
from typing import List, Union

import aiofiles
import xxhash
from fastapi import APIRouter, Depends, File, Path, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.scheduler import scheduler
from deciphon_api.models.db import DB, DBCreate, DBIDType, DBRead
from deciphon_api.models.hmm import HMM, HMMIDType

router = APIRouter()


mime = "application/octet-stream"


@router.get(
    "/dbs/{id}",
    summary="get db",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-db",
    deprecated=True,
)
async def get_db(
    id: Union[int, str] = Path(...), id_type: DBIDType = Query(DBIDType.DB_ID.value)
):
    return DB.get(id, id_type)


@router.get(
    "/dbs/{id}",
    summary="get db by id",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-db-by-id",
)
async def get_db_by_id(id: int = Path(..., gt=0)):
    return DB.get(id, DBIDType.DB_ID)


@router.get(
    "/dbs/xxh3/{xxh3}",
    summary="get db by xxh3",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-db-by-xxh3",
)
async def get_db_by_xxh3(xxh3: int):
    return DB.get(xxh3, DBIDType.XXH3)


@router.get(
    "/dbs/filename/{filename}",
    summary="get db by filename",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-db-by-filename",
)
async def get_db_by_filename(filename: str):
    return DB.get(filename, DBIDType.FILENAME)


@router.get(
    "/dbs/hmm-id/{hmm_id}",
    summary="get db by hmm_id",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-db-by-hmm_id",
)
async def get_db_by_hmm_id(hmm_id: int):
    return DB.get(hmm_id, DBIDType.HMM_ID)


@router.get(
    "/dbs",
    summary="get db list",
    response_model=List[DB],
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-db-list",
)
async def get_db_list():
    return DB.get_list()


@router.get(
    "/dbs/{db_id}/download",
    summary="download db",
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:download-db",
)
async def download_db(db_id: int = Path(..., gt=0)):
    db = DB.get(db_id, DBIDType.DB_ID)
    return FileResponse(db.filename, media_type=mime, filename=db.filename)


@router.post(
    "/dbs/",
    summary="upload a new db",
    response_model=DBRead,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="dbs:upload-db",
    dependencies=[Depends(auth_request)],
)
async def upload_db(
    db_file: UploadFile = File(..., content_type=mime, description="deciphon db"),
):

    h = xxhash.xxh3_64()
    async with aiofiles.open(db_file.filename, "wb") as file:
        while content := await db_file.read(4 * 1024 * 1024):
            h.update(content)
            await file.write(content)

    hmm = HMM.get(db_file.filename.replace("dcp", "hmm"), HMMIDType.FILENAME)
    db = DBCreate(
        filename=db_file.filename,
        xxh3=ctypes.c_int64(h.intdigest()).value,
        hmm_id=hmm.id,
    )
    with Session(scheduler) as session:
        x = DB.from_orm(db)
        session.add(x)
        session.commit()
        session.refresh(x)
        return x
    # DBCreate
    # return DB.add(db_file.filename)


@router.delete(
    "/dbs/{db_id}",
    summary="remove db",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:remove-db",
    dependencies=[Depends(auth_request)],
)
async def remove_db(db_id: int = Path(..., gt=0)):
    DB.remove(db_id)
    return JSONResponse({})
