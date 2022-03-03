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
from ..rc import RC
from ..seq import Seq

router = APIRouter()


@router.get(
    "/seqs/{seq_id}",
    summary="get sequence",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def httpget_seqs_xxx(seq_id: int):
    cseq = ffi.new("struct sched_seq *")
    cseq[0].id = seq_id

    rc = RC(lib.sched_seq_get(cseq))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return Seq.from_cdata(cseq)
