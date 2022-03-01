from enum import Enum, IntEnum

from pydantic import BaseModel

from .logger import logger


class RC(IntEnum):
    OK = 0
    END = 1
    NOTFOUND = 2
    EFAIL = 3
    EIO = 4
    EINVAL = 5
    ENOMEM = 6
    EPARSE = 7


class Code(str, Enum):
    OK = "ok"
    END = "end"
    NOTFOUND = "notfound"
    EFAIL = "efail"
    EIO = "eio"
    EINVAL = "einval"
    ENOMEM = "enomem"
    EPARSE = "eparse"


class ReturnData(BaseModel):
    rc: Code = Code.OK
    msg: str = ""


def retdata(rc: RC) -> ReturnData:
    return ReturnData(rc=Code[RC(rc).name], msg=logger.pop())
