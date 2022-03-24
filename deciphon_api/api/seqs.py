from fastapi import APIRouter, Path
from starlette.status import HTTP_200_OK

from deciphon_api.api.responses import responses
from deciphon_api.models.seq import Seq

router = APIRouter()


@router.get(
    "/seqs/{seq_id}",
    summary="get sequence",
    response_model=Seq,
    status_code=HTTP_200_OK,
    responses=responses,
    name="seqs:get-sequence",
)
def get_sequence(seq_id: int = Path(..., gt=0)):
    return Seq.from_id(seq_id)
