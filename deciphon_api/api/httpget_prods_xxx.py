from typing import List

from fastapi import APIRouter
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .._types import ErrorResponse
from ..csched import ffi, lib
from ..exception import EINVALException, create_exception
from ..prod import Prod
from ..rc import RC

router = APIRouter()


@router.get(
    "/prods/{prod_id}",
    summary="get product",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_prods_xxx(prod_id: int):
    cprod = ffi.new("struct sched_prod *")
    cprod[0].id = prod_id

    rc = RC(lib.sched_prod_get(cprod))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise EINVALException(HTTP_404_NOT_FOUND, "prod not found")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return [Prod.from_cdata(cprod)]
