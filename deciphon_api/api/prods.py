import os
from typing import List

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import PlainTextResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api._types import ErrorResponse
from deciphon_api.csched import lib
from deciphon_api.examples import prods_file
from deciphon_api.exception import EINVALException, EPARSEException, create_exception
from deciphon_api.models.prod import Prod
from deciphon_api.rc import RC

router = APIRouter()


@router.get(
    "/prods/{prod_id}",
    summary="get product",
    response_model=Prod,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="prods:get-product",
)
def get_product(prod_id: int):
    return Prod.from_id(prod_id)


@router.post(
    "/prods/",
    summary="upload file of products",
    response_model=List,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="prods:upload-products",
)
def upload_products(
    prods_file: UploadFile = File(
        ..., content_type="text/tab-separated-values", description="file of products"
    )
):
    prods_file.file.flush()
    fd = os.dup(prods_file.file.fileno())
    fp = lib.fdopen(fd, b"rb")

    rc = RC(lib.sched_prod_add_file(fp))
    assert rc != RC.END

    if rc == RC.EINVAL:
        raise EINVALException(HTTP_409_CONFLICT, "constraint violation")

    if rc == RC.EPARSE:
        raise EPARSEException(HTTP_400_BAD_REQUEST, "failed to parse file")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return []


@router.get("/prods/upload/example", response_class=PlainTextResponse)
def httpget_prods_upload_example():
    return prods_file
