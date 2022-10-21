from typing import List, Union

import aiofiles
from fastapi import APIRouter, Depends, File, Path, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.dbs import get_db_by_hmm_id
from deciphon_api.api.responses import responses
from deciphon_api.models.db import DB
from deciphon_api.models.hmm import HMM, HMMIDType

router = APIRouter()


mime = "text/plain"


@router.get(
    "/hmms/{id}",
    summary="get hmm",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm",
    deprecated=True,
)
async def get_hmm(
    id: Union[int, str] = Path(...), id_type: HMMIDType = Query(HMMIDType.HMM_ID.value)
):
    return HMM.get(id, id_type)


@router.get(
    "/hmms/{id}",
    summary="get hmm by id",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm-by-id",
)
async def get_hmm_by_id(id: int = Path(..., gt=0)):
    return HMM.get(id, HMMIDType.HMM_ID)


@router.get(
    "/hmms/xxh3/{xxh3}",
    summary="get hmm by xxh3",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm-by-xxh3",
)
async def get_hmm_by_xxh3(xxh3: int):
    return HMM.get(xxh3, HMMIDType.XXH3)


@router.get(
    "/hmms/job-id/{job_id}",
    summary="get hmm by job_id",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm-by-job-id",
)
async def get_hmm_by_job_id(job_id: int = Path(..., gt=0)):
    return HMM.get(job_id, HMMIDType.JOB_ID)


@router.get(
    "/hmms/filename/{filename}",
    summary="get hmm by filename",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm-by-filename",
)
async def get_hmm_by_filename(filename: str):
    return HMM.get(filename, HMMIDType.FILENAME)


get_db_by_hmm_id = router.get(
    "/hmms/{hmm_id}/db",
    summary="get db by hmm_id",
    response_model=DB,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-db-by-hmm-id",
)(get_db_by_hmm_id)


@router.get(
    "/hmms",
    summary="get hmm list",
    response_model=List[HMM],
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-hmm-list",
)
async def get_hmm_list():
    return HMM.get_list()


@router.get(
    "/hmms/{hmm_id}/download",
    summary="download hmm",
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:download-hmm",
)
async def download_hmm(hmm_id: int = Path(..., gt=0)):
    hmm = HMM.get(hmm_id, HMMIDType.HMM_ID)
    return FileResponse(hmm.filename, media_type=mime, filename=hmm.filename)


@router.post(
    "/hmms/",
    summary="upload a new hmm",
    response_model=HMM,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="hmms:upload-hmm",
    dependencies=[Depends(auth_request)],
)
async def upload_hmm(
    hmm_file: UploadFile = File(..., content_type=mime, description="hmmer3 file"),
):
    async with aiofiles.open(hmm_file.filename, "wb") as file:
        while content := await hmm_file.read(4 * 1024 * 1024):
            await file.write(content)

    return HMM.submit(hmm_file.filename)


@router.delete(
    "/hmms/{hmm_id}",
    summary="remove hmm",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:remove-hmm",
    dependencies=[Depends(auth_request)],
)
async def remove_hmm(
    hmm_id: int = Path(..., gt=0),
):
    HMM.remove(hmm_id)
    return JSONResponse({})
