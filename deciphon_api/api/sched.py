from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import UnauthorizedError
from deciphon_api.models.sched_health import SchedHealth
from deciphon_api.sched.sched import sched_wipe

router = APIRouter()


@router.delete(
    "/sched/wipe",
    summary="wipe sched",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="sched:wipe",
)
def wipe(authenticated: bool = Depends(auth_request)):
    if not authenticated:
        raise UnauthorizedError()

    sched_wipe()
    return JSONResponse([])


@router.get(
    "/sched/check_health",
    summary="check health",
    response_model=SchedHealth,
    status_code=HTTP_200_OK,
    responses=responses,
    name="sched:check-health",
)
def check_health(authenticated: bool = Depends(auth_request)):
    if not authenticated:
        raise UnauthorizedError()

    health = SchedHealth()
    health.check()
    return health
