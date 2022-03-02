from typing import List

from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .prod import Prod
from .rc import RC, StrRC
from ._types import ErrorResponse


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

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "job not found")

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return prods
