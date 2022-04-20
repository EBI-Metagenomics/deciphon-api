from typing import List

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
    return Seq.get(seq_id)


@router.get(
    "/seqs",
    summary="get seq list",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses=responses,
    name="seqs:get-seq-list",
)
def get_seq_list():
    return Seq.get_list()
