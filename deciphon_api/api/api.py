from fastapi import APIRouter, Request
from starlette.status import HTTP_200_OK

from deciphon_api.api import (
    dbs_priv,
    dbs_pub,
    hmms_priv,
    hmms_pub,
    jobs_priv,
    jobs_pub,
    scans_priv,
    scans_pub,
)
from deciphon_api.responses import PrettyJSONResponse

router = APIRouter()

router.include_router(dbs_priv.router)
router.include_router(dbs_pub.router)
router.include_router(hmms_priv.router)
router.include_router(hmms_pub.router)
router.include_router(jobs_priv.router)
router.include_router(jobs_pub.router)
router.include_router(scans_priv.router)
router.include_router(scans_pub.router)


@router.get(
    "/",
    summary="list of all endpoints",
    response_class=PrettyJSONResponse,
    status_code=HTTP_200_OK,
    name="root:list-of-endpoints",
)
def root(request: Request):
    routes = sorted(request.app.routes, key=lambda x: x.name)
    urls = {route.name: route.path for route in routes}
    return PrettyJSONResponse(urls)
