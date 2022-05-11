from typing import Union

from deciphon_sched.cffi import lib
from deciphon_sched.error import SchedError
from deciphon_sched.rc import RC as SchedRC
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_418_IM_A_TEAPOT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from deciphon_api.core.rc import RC

__all__ = [
    "ErrorResponse",
    "InvalidTypeError",
    "sched_error_handler",
    "http422_error_handler",
    "http_error_handler",
]


class InvalidTypeError(HTTPException):
    def __init__(self, expected_type: str):
        super().__init__(HTTP_406_NOT_ACCEPTABLE, f"Expected {expected_type} type")


def truncate(msg: str):
    limit = int(lib.SCHED_JOB_ERROR_SIZE)
    return (msg[: limit - 3] + "...") if len(msg) > limit else msg


class ErrorResponse(BaseModel):
    rc: Union[SchedRC, RC]
    msg: str

    class Config:
        use_enum_values = False

    @classmethod
    def create(cls, rc: Union[SchedRC, RC], msg: str):
        return cls(rc=rc, msg=truncate(msg))


def sched_error_handler(_: Request, exc: SchedError) -> JSONResponse:
    content = ErrorResponse.create(exc.rc, exc.msg)

    http_code = HTTP_418_IM_A_TEAPOT

    if exc.rc == SchedRC.SCHED_DB_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif exc.rc == SchedRC.SCHED_HMM_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif exc.rc == SchedRC.SCHED_JOB_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif exc.rc == SchedRC.SCHED_PROD_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif exc.rc == SchedRC.SCHED_SEQ_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif exc.rc == SchedRC.SCHED_SCAN_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND

    return JSONResponse(
        status_code=http_code,
        content=content.dict(),
    )


def http422_error_handler(
    _: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    content = ErrorResponse.create(RC.API_VALIDATION_ERROR, str(exc))

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=content.dict(),
    )


def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    content = ErrorResponse.create(RC.API_HTTP_ERROR, exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=content.dict(),
    )
