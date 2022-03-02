from fastapi import Request
from fastapi.responses import JSONResponse

from ._app import app
from .rc import StrRC

__all__ = ["DCPException"]


class DCPException(Exception):
    def __init__(self, http_code: int, code: StrRC, msg: str = ""):
        self.http_code = http_code
        self.code = code
        self.msg = msg


@app.exception_handler(DCPException)
def deciphon_exception_handler(_: Request, exc: DCPException):
    return JSONResponse(
        status_code=exc.http_code,
        content={"rc": exc.code, "msg": exc.msg},
    )
