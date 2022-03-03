from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from .csched import lib
from .exception import create_exception
from .rc import RC

__all__ = ["sched_setup", "sched_open", "sched_close"]


def sched_setup(file_name: str):
    rc = RC(lib.sched_setup(file_name.encode()))

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)


def sched_open():
    rc = RC(lib.sched_open())

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)


def sched_close():
    rc = RC(lib.sched_close())

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)
