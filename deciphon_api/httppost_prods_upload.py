import os

from fastapi import File, UploadFile
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from ._types import ErrorResponse
from .csched import lib
from .exception import EINVALException, EPARSEException, create_exception
from .rc import RC


@app.post(
    "/prods/upload",
    summary="upload a text/tab-separated-values file of products",
    # response_model=ErrorResponse,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        HTTP_409_CONFLICT: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httppost_prods_upload(prods_file: UploadFile = File(...)):
    prods_file.file.flush()
    fd = os.dup(prods_file.file.fileno())
    fp = lib.fdopen(fd, b"rb")
    rc = RC(lib.sched_prod_add_file(fp))

    if rc == RC.EINVAL:
        raise EINVALException(HTTP_409_CONFLICT, "constraint violation")

    if rc == RC.EPARSE:
        raise EPARSEException(HTTP_400_BAD_REQUEST, "failed to parse file")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return {}
