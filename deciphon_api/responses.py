from .rc import Code, ReturnData
from fastapi.responses import JSONResponse

__all__ = ["json_response"]


def json_response(status_code: int, rc: Code, msg: str = ""):
    return JSONResponse(
        status_code=status_code,
        content=ReturnData(rc=rc, msg=msg),
    )
