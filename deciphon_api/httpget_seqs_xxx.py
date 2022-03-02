from typing import List

from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .rc import RC, StrRC
from ._types import ErrorResponse
from .seq import Seq


@app.get(
    "/seqs/{seq_id}",
    summary="get sequence",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def seqs_xxx(seq_id: int):
    cseq = ffi.new("struct sched_seq *")
    cseq[0].id = seq_id

    rc = RC(lib.sched_seq_get(cseq))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        return []

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return Seq.from_cdata(cseq)
