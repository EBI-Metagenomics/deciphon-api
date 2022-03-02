from enum import Enum, IntEnum

from fastapi import HTTPException, status
from pydantic import BaseModel

from .csched import lib
from .rc import StrRC, retdata


class JS(IntEnum):
    SCHED_JOB_PEND = 0
    SCHED_JOB_RUN = 1
    SCHED_JOB_DONE = 2
    SCHED_JOB_FAIL = 3


class JobState(str, Enum):
    SCHED_JOB_PEND = "pend"
    SCHED_JOB_RUN = "run"
    SCHED_JOB_DONE = "done"
    SCHED_JOB_FAIL = "fail"


class DB(BaseModel):
    id: int
    name: str


class PendJob(BaseModel):
    id: int = 0
    db_id: int = 0
    multi_hits: bool = False
    hmmer3_compat: bool = False


def sched_setup():
    rd = retdata(lib.sched_setup(b"deciphon.sched"))

    if rd.rc != StrRC.OK:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, rd)


def sched_open():
    rd = retdata(lib.sched_open())

    if rd.rc != StrRC.OK:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, rd)


def sched_close():
    rd = retdata(lib.sched_close())

    if rd.rc != StrRC.OK:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, rd)

    return rd


class Sched:
    def __init__(self) -> None:
        sched_setup()
        sched_open()

    def close(self) -> None:
        sched_close()


sched = Sched()
