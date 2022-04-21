from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.rc import RC

__all__ = ["SchedError", "SchedWrapperError"]


def sched_error_string(rc: RC) -> str:
    return ffi.string(lib.sched_error_string(rc.value))


class SchedError(Exception):
    def __init__(self, rc: RC):
        self.rc: RC = rc
        self.msg: str = sched_error_string(rc)


class SchedWrapperError(SchedError):
    def __init__(self, rc: RC):
        self.rc: RC = rc
        self.msg: str = sched_error_string(rc)
