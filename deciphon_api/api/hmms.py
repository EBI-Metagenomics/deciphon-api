import shutil
from typing import List

from fastapi import APIRouter, File, Path, UploadFile
from fastapi.responses import FileResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.responses import responses
from deciphon_api.models.hmm import HMM

router = APIRouter()


mime = "application/octet-stream"


@router.get(
    "/hmms/{hmm_id}",
    summary="get hmm",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm",
)
def get_hmm(hmm_id: int = Path(..., gt=0)):
    return HMM.get_by_id(hmm_id)


@router.get(
    "/hmms",
    summary="get hmm list",
    response_model=List[HMM],
    status_code=HTTP_200_OK,
    responses=responses,
    name="dbs:get-hmm-list",
)
def get_hmm_list():
    return HMM.get_list()


@router.get(
    "/hmms/{hmm_id}/download",
    summary="download hmm",
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:download-hmm",
)
def download_hmm(hmm_id: int = Path(..., gt=0)):
    hmm = HMM.get_by_id(hmm_id)
    return FileResponse(hmm.filename, media_type=mime, filename=hmm.filename)


@router.post(
    "/hmms/",
    summary="upload a new hmm",
    response_model=HMM,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="hmms:upload-hmm",
)
def upload_hmm(
    hmm: UploadFile = File(..., content_type=mime, description="hmmer3 file")
):
    with open(hmm.filename, "wb") as dst:
        shutil.copyfileobj(hmm.file, dst)
    return HMM.submit(hmm.filename)
