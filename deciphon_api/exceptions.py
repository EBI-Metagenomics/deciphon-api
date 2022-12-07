from typing import Type

from fastapi import HTTPException
from sqlmodel import SQLModel
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

__all__ = ["NotFoundException", "ConflictException"]


class NotFoundException(HTTPException):
    def __init__(self, T: Type[SQLModel]):
        super().__init__(HTTP_404_NOT_FOUND, f"{T.__name__} not found")


class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(HTTP_409_CONFLICT, f"SQL constraint ({detail})")
