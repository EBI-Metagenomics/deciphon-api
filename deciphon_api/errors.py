from .rc import RC

__all__ = [
    "DCPException",
    "EFAILException",
    "EINVALException",
    "EIOException",
    "ENOMEMException",
    "EPARSEException",
    "create_exception",
]


class DCPException(Exception):
    def __init__(self, http_code: int, rc: RC, msg: str = ""):
        self.http_code = http_code
        self.rc = rc
        self.msg = msg


class EFAILException(DCPException):
    def __init__(self, http_code: int, msg: str = "unspecified failure"):
        super().__init__(http_code, RC.EFAIL, msg)


class EIOException(DCPException):
    def __init__(self, http_code: int, msg: str = "io failure"):
        super().__init__(http_code, RC.EIO, msg)


class EINVALException(DCPException):
    def __init__(self, http_code: int, msg: str = "invalid value"):
        super().__init__(http_code, RC.EINVAL, msg)


class ENOMEMException(DCPException):
    def __init__(self, http_code: int, msg: str = "not enough memory"):
        super().__init__(http_code, RC.ENOMEM, msg)


class EPARSEException(DCPException):
    def __init__(self, http_code: int, msg: str = "parse error"):
        super().__init__(http_code, RC.EPARSE, msg)


def create_exception(http_code: int, rc: RC) -> DCPException:
    assert rc != RC.OK
    assert rc != RC.END
    assert rc != RC.NOTFOUND

    if rc == RC.EFAIL:
        return EFAILException(http_code)
    elif rc == RC.EIO:
        return EIOException(http_code)
    elif rc == RC.EINVAL:
        return EINVALException(http_code)
    elif rc == RC.ENOMEM:
        return ENOMEMException(http_code)
    else:
        assert rc == RC.EPARSE
        return EPARSEException(http_code)
