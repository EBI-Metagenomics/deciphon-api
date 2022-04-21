import shutil
from typing import List, Union

from fastapi import APIRouter, Depends, File, Path, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import UnauthorizedError
from deciphon_api.models.hmm import HMM, HMMIDType

router = APIRouter()


mime = "application/octet-stream"


@router.get(
    "/hmms/{id}",
    summary="get hmm",
    response_model=HMM,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:get-hmm",
)
def get_hmm(
    id: Union[int, str] = Path(...), id_type: HMMIDType = Query(HMMIDType.HMM_ID.value)
):
    return HMM.get(id, id_type)


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
    hmm = HMM.get(hmm_id, HMMIDType.HMM_ID)
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
    hmm_file: UploadFile = File(..., content_type=mime, description="hmmer3 file"),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    with open(hmm_file.filename, "wb") as dst:
        shutil.copyfileobj(hmm_file.file, dst)

    return HMM.submit(hmm_file.filename)


@router.delete(
    "/hmms/{hmm_id}",
    summary="remove hmm",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="hmms:remove-hmm",
)
def remove_hmm(
    hmm_id: int = Path(..., gt=0),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    HMM.remove(hmm_id)
    return JSONResponse({})
