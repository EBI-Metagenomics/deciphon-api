from fastapi import Request
from fastapi.responses import JSONResponse

from ._app import app
from .rc import Code

__all__ = ["DCPException"]


class DCPException(Exception):
    def __init__(self, status_code: int, code: Code, msg: str = ""):
        self.status_code = status_code
        self.code = code
        self.msg = msg


@app.exception_handler(DCPException)
def deciphon_exception_handler(_: Request, exc: DCPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"rc": exc.code, "msg": exc.msg},
    )
