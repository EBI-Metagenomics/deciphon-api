from fastapi import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

__all__ = ["HMMNotFoundError", "ConflictError", "FileNotInStorageError"]


class HMMNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(HTTP_404_NOT_FOUND, "HMM not found")


class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(HTTP_409_CONFLICT, f"SQL constraint ({detail})")


class FileNotInStorageError(HTTPException):
    def __init__(self, sha256: str):
        super().__init__(
            HTTP_422_UNPROCESSABLE_ENTITY,
            f"File (SHA256: {sha256}) not found in storage",
        )
