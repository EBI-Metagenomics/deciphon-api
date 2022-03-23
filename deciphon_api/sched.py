from loguru import logger
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import create_exception
from deciphon_api.rc import RC

__all__ = ["sched_setup", "sched_open", "sched_close"]


def sched_setup(file_name: str):
    lib.sched_logger_setup(lib.sched_logger_print, ffi.NULL)

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


@ffi.def_extern()
def sched_logger_print(ctx: bytes, msg: bytes, _):
    logger.error(ffi.string(ctx).decode() + ": " + ffi.string(msg).decode())
