from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from deciphon_api.csched import lib
from deciphon_api.errors import ErrorResponse, InternalError
from deciphon_api.api.responses import responses
from deciphon_api.rc import RC

router = APIRouter()


@router.delete(
    "/",
    summary="wipe database",
    description="wipe database",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpdelete():
    rc = RC(lib.sched_wipe())

    if rc != RC.OK:
        raise InternalError(rc)

    return JSONResponse([])
