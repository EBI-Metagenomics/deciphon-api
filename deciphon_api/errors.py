from fastapi import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse

__all__ = [
    "integrity_error_handler",
    "HMMNotFoundError",
    "JobNotFoundError",
    "DBNotFoundError",
    "FileNotInStorageError",
    "NotFoundInDBError",
]


async def integrity_error_handler(_: Request, exc: IntegrityError):
    return JSONResponse(
        content={"detail": str(exc)}, status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )


class NotFoundInDBError(HTTPException):
    def __init__(self, name: str):
        super().__init__(HTTP_404_NOT_FOUND, f"{name} not found")


class HMMNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(HTTP_404_NOT_FOUND, "HMM not found")


class JobNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(HTTP_404_NOT_FOUND, "Job not found")


class DBNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(HTTP_404_NOT_FOUND, "DB not found")


class FileNotInStorageError(HTTPException):
    def __init__(self, sha256: str):
        super().__init__(
            HTTP_422_UNPROCESSABLE_ENTITY,
            f"File (SHA256: {sha256}) not found in storage",
        )
