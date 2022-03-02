from pydantic import BaseModel

from .rc import RC, StrRC

__all__ = ["ErrorResponse"]


class ErrorResponse(BaseModel):
    rc: StrRC = StrRC.EFAIL
    msg: str = "something went wrong"

    def __init__(self, rc: RC, msg: str):
        self.rc = StrRC[rc.name]
        self.msg = msg
