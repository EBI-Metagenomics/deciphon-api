from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT


class NotFoundException(HTTPException):
    def __init__(self, item: str):
        super().__init__(HTTP_404_NOT_FOUND, f"{item} not found")


class HMMNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("HMM")


class DBNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("DB")


class ScanNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Scan")


class SeqNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Scan")


class JobNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Job")


class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(HTTP_409_CONFLICT, f"SQL constraint ({detail})")
