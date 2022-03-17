import os
from typing import List

from fastapi import APIRouter, File, UploadFile
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .._types import ErrorResponse
from ..csched import lib
from ..exception import EINVALException, EPARSEException, create_exception
from ..rc import RC

router = APIRouter()


@router.post(
    "/prods/",
    summary="upload a products file",
    response_model=List,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppost_prods_upload(
    prods_file: UploadFile = File(
        ..., content_type="text/tab-separated-values", description="products file"
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
