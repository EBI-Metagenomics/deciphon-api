import json
from typing import Optional, Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.rc import RC, StrRC
from deciphon_api.sched.cffi import lib

__all__ = [
    "ConflictError",
    "NotFoundError",
    "DeciphonError",
    "EFAIL",
    "EINVAL",
    "EIO",
    "ENOMEM",
    "EPARSE",
    "ECONSTRAINT",
    "ErrorResponse",
    "InternalError",
    "ForbiddenError",
    "ParseError",
    "ConditionError",
    "UnauthorizedError",
    "ConstraintError",
    "InvalidTypeError",
]


class DeciphonError(Exception):
    def __init__(self, http_code: int, rc: RC, msg: str = ""):
        self.http_code = http_code
        self.rc = rc
        self.msg = msg


class EFAIL(DeciphonError):
    def __init__(self, http_code: int, msg: str = "unspecified failure"):
        super().__init__(http_code, RC.EFAIL, msg)


class EIO(DeciphonError):
    def __init__(self, http_code: int, msg: str = "io failure"):
        super().__init__(http_code, RC.EIO, msg)


class EINVAL(DeciphonError):
    def __init__(self, http_code: int, msg: str = "invalid value"):
        super().__init__(http_code, RC.EINVAL, msg)


class ENOMEM(DeciphonError):
    def __init__(self, http_code: int, msg: str = "not enough memory"):
        super().__init__(http_code, RC.ENOMEM, msg)


class EPARSE(DeciphonError):
    def __init__(self, http_code: int, msg: str = "parse error"):
        super().__init__(http_code, RC.EPARSE, msg)


class ECONSTRAINT(DeciphonError):
    def __init__(self, http_code: int, msg: str = "constraint error"):
        super().__init__(http_code, RC.ECONSTRAINT, msg)


class ParseError(EPARSE):
    def __init__(self, msg: str):
        super().__init__(HTTP_400_BAD_REQUEST, msg)


class NotFoundError(EINVAL):
    def __init__(self, what: str):
        super().__init__(HTTP_404_NOT_FOUND, f"{what} not found")


class ConflictError(EINVAL):
    def __init__(self, msg: str):
        super().__init__(HTTP_409_CONFLICT, msg)


class UnauthorizedError(EINVAL):
    def __init__(self):
        super().__init__(HTTP_401_UNAUTHORIZED, "Failed to validate credentials")


class ForbiddenError(EINVAL):
    def __init__(self, msg: str):
        super().__init__(HTTP_403_FORBIDDEN, msg)


class ConstraintError(ECONSTRAINT):
    def __init__(self, msg: str):
        super().__init__(HTTP_403_FORBIDDEN, msg)


class ConditionError(EINVAL):
    def __init__(self, msg: str):
        super().__init__(HTTP_412_PRECONDITION_FAILED, msg)


class InvalidTypeError(EINVAL):
    def __init__(self, msg: str):
        super().__init__(HTTP_412_PRECONDITION_FAILED, msg)


def InternalError(rc: RC, msg: Optional[str] = None) -> DeciphonError:
    assert rc != RC.OK
    assert rc != RC.END
    assert rc != RC.NOTFOUND

    http_code = HTTP_500_INTERNAL_SERVER_ERROR
    kwargs = {}
    if msg is not None:
        kwargs["msg"] = msg

    if rc == RC.EFAIL:
        return EFAIL(http_code, **kwargs)
    elif rc == RC.EIO:
        return EIO(http_code, **kwargs)
    elif rc == RC.EINVAL:
        return EINVAL(http_code, **kwargs)
    elif rc == RC.ENOMEM:
        return ENOMEM(http_code, **kwargs)
    else:
        assert rc == RC.EPARSE
        return EPARSE(http_code, **kwargs)


def truncate(msg: str):
    limit = int(lib.JOB_ERROR_SIZE)
    return (msg[: limit - 3] + "...") if len(msg) > limit else msg


class ErrorResponse(BaseModel):
    rc: StrRC = StrRC.EFAIL
    msg: str = "something went wrong"

    @classmethod
    def create(cls, rc: RC, msg: str):
        return cls(rc=StrRC[rc.name], msg=truncate(msg))


def deciphon_error_handler(_: Request, exc: DeciphonError):
    content = ErrorResponse.create(exc.rc, exc.msg)
    return JSONResponse(
        status_code=exc.http_code,
        content=content.dict(),
    )


def http422_error_handler(
    _: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    content = ErrorResponse.create(RC.EINVAL, json.dumps(exc.errors()))
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=content.dict(),
    )
