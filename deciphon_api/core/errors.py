from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_418_IM_A_TEAPOT,
)

from deciphon_api.sched.cffi import lib
from deciphon_api.sched.error import SchedError
from deciphon_api.sched.rc import RC

__all__ = [
    "UnauthorizedError",
    "ErrorResponse",
    "InvalidTypeError",
]


class UnauthorizedError(HTTPException):
    def __init__(self):
        super().__init__(HTTP_401_UNAUTHORIZED, "Failed to validate credentials")


class InvalidTypeError(HTTPException):
    def __init__(self, expected_type: str):
        super().__init__(HTTP_406_NOT_ACCEPTABLE, f"Expected {expected_type} type")


def truncate(msg: str):
    limit = int(lib.JOB_ERROR_SIZE)
    return (msg[: limit - 3] + "...") if len(msg) > limit else msg


class ErrorResponse(BaseModel):
    rc: RC
    msg: str

    class Config:
        use_enum_values = False

    @classmethod
    def create(cls, rc: RC, msg: str):
        return cls(rc=rc, msg=truncate(msg))


def sched_error_handler(_: Request, exc: SchedError):
    content = ErrorResponse.create(exc.rc, exc.msg)

    http_code = HTTP_418_IM_A_TEAPOT

    if content.rc == RC.SCHED_DB_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif content.rc == RC.SCHED_HMM_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif content.rc == RC.SCHED_JOB_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif content.rc == RC.SCHED_PROD_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif content.rc == RC.SCHED_SEQ_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND
    elif content.rc == RC.SCHED_SCAN_NOT_FOUND:
        http_code = HTTP_404_NOT_FOUND

    return JSONResponse(
        status_code=http_code,
        content=content.dict(),
    )
