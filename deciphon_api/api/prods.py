import os
from typing import List

from fastapi import APIRouter, Depends, File, Path, UploadFile
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import (
    ConflictError,
    InternalError,
    ParseError,
    UnauthorizedError,
)
from deciphon_api.models.prod import Prod
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

router = APIRouter()


@router.get(
    "/prods/{prod_id}",
    summary="get product",
    response_model=Prod,
    status_code=HTTP_200_OK,
    responses=responses,
    name="prods:get-product",
)
def get_product(prod_id: int = Path(..., gt=0)):
    return Prod.from_id(prod_id)


@router.get(
    "/prods",
    summary="get prod list",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses=responses,
    name="prods:get-prod-list",
)
def get_prod_list():
    return Prod.get_list()


@router.post(
    "/prods/",
    summary="upload file of products",
    response_model=List,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="prods:upload-products",
)
def upload_products(
    prods_file: UploadFile = File(
        ..., content_type="text/tab-separated-values", description="file of products"
    ),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    prods_file.file.flush()
    fd = os.dup(prods_file.file.fileno())
    if fd == -1:
        raise InternalError(RC.EFAIL, "Failed to duplicate file descriptor.")

    fp = lib.fdopen(fd, b"rb")
    if fp == ffi.NULL:
        raise InternalError(RC.EFAIL, "Failed to fdopen a file descriptor.")

    try:
        rc = RC(lib.sched_prod_add_file(fp))
        assert rc != RC.END

        if rc == RC.EINVAL:
            raise ConflictError("constraint violation")

        if rc == RC.EPARSE:
            raise ParseError("failed to parse file")

        if rc != RC.OK:
            raise InternalError(rc)
    finally:
        lib.fclose(fp)

    return []
