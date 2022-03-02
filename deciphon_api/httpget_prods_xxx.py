from typing import List

from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .prod import Prod
from .rc import RC, Code, ReturnData


@app.get(
    "/prods/{prod_id}",
    summary="get product",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def prods_xxx(prod_id: int):
    cprod = ffi.new("struct sched_prod *")
    cprod[0].id = prod_id

    rc = RC(lib.sched_prod_get(cprod))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return [Prod.from_cdata(cprod)]
