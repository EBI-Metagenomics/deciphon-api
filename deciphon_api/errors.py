from pydantic import BaseModel
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.rc import RC, StrRC

__all__ = [
    "DBAlreadyExists",
    "DBNotFound",
    "DCPException",
    "EFAIL",
    "EINVAL",
    "EIO",
    "ENOMEM",
    "EPARSE",
    "ErrorResponse",
    "FileNotFound",
    "InternalError",
]


class DCPException(Exception):
    def __init__(self, http_code: int, rc: RC, msg: str = ""):
        self.http_code = http_code
        self.rc = rc
        self.msg = msg


class EFAIL(DCPException):
    def __init__(self, http_code: int, msg: str = "unspecified failure"):
        super().__init__(http_code, RC.EFAIL, msg)


class EIO(DCPException):
    def __init__(self, http_code: int, msg: str = "io failure"):
        super().__init__(http_code, RC.EIO, msg)


class EINVAL(DCPException):
    def __init__(self, http_code: int, msg: str = "invalid value"):
        super().__init__(http_code, RC.EINVAL, msg)


class ENOMEM(DCPException):
    def __init__(self, http_code: int, msg: str = "not enough memory"):
        super().__init__(http_code, RC.ENOMEM, msg)


class EPARSE(DCPException):
    def __init__(self, http_code: int, msg: str = "parse error"):
        super().__init__(http_code, RC.EPARSE, msg)


class DBNotFound(EINVAL):
    def __init__(self):
        super().__init__(HTTP_404_NOT_FOUND, "database not found")


class FileNotFound(EINVAL):
    def __init__(self):
        super().__init__(HTTP_412_PRECONDITION_FAILED, "file not found")


class DBAlreadyExists(EINVAL):
    def __init__(self):
        super().__init__(HTTP_409_CONFLICT, "database already exists")


def InternalError(rc: RC) -> DCPException:
    assert rc != RC.OK
    assert rc != RC.END
    assert rc != RC.NOTFOUND

    http_code = HTTP_500_INTERNAL_SERVER_ERROR

    if rc == RC.EFAIL:
        return EFAIL(http_code)
    elif rc == RC.EIO:
        return EIO(http_code)
    elif rc == RC.EINVAL:
        return EINVAL(http_code)
    elif rc == RC.ENOMEM:
        return ENOMEM(http_code)
    else:
        assert rc == RC.EPARSE
        return EPARSE(http_code)


class ErrorResponse(BaseModel):
    rc: StrRC = StrRC.EFAIL
    msg: str = "something went wrong"

    @classmethod
    def create(cls, rc: RC, msg: str):
        return cls(rc=StrRC[rc.name], msg=msg)
