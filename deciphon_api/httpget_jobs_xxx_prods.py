from typing import List

from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from ._types import ErrorResponse
from .csched import ffi, lib
from .exception import EINVALException, create_exception
from .prod import Prod
from .rc import RC


@app.get(
    "/jobs/{job_id}/prods",
    summary="get products",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_jobs_xxx_prods(job_id: int):
    cprod = ffi.new("struct sched_prod *")

    prods: List[Prod] = []
    rc = RC(
        lib.sched_job_get_prods(
            job_id, lib.append_prod_callback, cprod, ffi.new_handle(prods)
        )
    )
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return prods
