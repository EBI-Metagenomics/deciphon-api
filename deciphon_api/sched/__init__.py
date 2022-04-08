from loguru import logger

from deciphon_api.sched.cffi import ffi, lib

__all__ = ["sched_init", "sched_cleanup"]


def sched_init(file_name: str):
    from deciphon_api.core.errors import InternalError
    from deciphon_api.rc import RC

    lib.sched_logger_setup(lib.sched_logger_print, ffi.NULL)

    rc = RC(lib.sched_init(file_name.encode()))

    if rc != RC.OK:
        raise InternalError(rc)


def sched_cleanup():
    from deciphon_api.core.errors import InternalError
    from deciphon_api.rc import RC

    rc = RC(lib.sched_cleanup())

    if rc != RC.OK:
        raise InternalError(rc)


@ffi.def_extern()
def sched_logger_print(ctx: bytes, msg: bytes, _):
    logger.error(ffi.string(ctx).decode() + ": " + ffi.string(msg).decode())