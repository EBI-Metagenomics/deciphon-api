from deciphon_sched.sched import sched_wipe
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.models.sched_health import SchedHealth

router = APIRouter()


@router.delete(
    "/sched/wipe",
    summary="wipe sched",
    response_class=JSONResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="sched:wipe",
    dependencies=[Depends(auth_request)],
)
async def wipe():
    sched_wipe()
    return JSONResponse([])


@router.get(
    "/sched/check-health",
    summary="check health",
    response_model=SchedHealth,
    status_code=HTTP_200_OK,
    responses=responses,
    name="sched:check-health",
    dependencies=[Depends(auth_request)],
)
async def check_health():
    health = SchedHealth()
    health.check()
    return health
