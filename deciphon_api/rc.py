from enum import Enum, IntEnum

from pydantic import BaseModel

from .logger import logger


class RC(IntEnum):
    DONE = 0
    END = 1
    NEXT = 2
    NOTFOUND = 3
    EFAIL = 4
    EINVAL = 5
    EIO = 6
    ENOMEM = 7
    EPARSE = 8


class Code(str, Enum):
    DONE = "done"
    END = "end"
    NEXT = "next"
    NOTFOUND = "notfound"
    EFAIL = "efail"
    EINVAL = "einval"
    EIO = "eio"
    ENOMEM = "enomem"
    EPARSE = "eparse"


class ReturnData(BaseModel):
    rc: Code = Code.DONE
    msg: str = ""


def retdata(rc: RC) -> ReturnData:
    return ReturnData(rc=Code[RC(rc).name], msg=logger.pop())
