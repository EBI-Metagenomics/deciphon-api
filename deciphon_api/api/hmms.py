from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter
from deciphon_api.storage import storage_has
from deciphon_api.api.id import IDPath
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from typing import List

from deciphon_api.api.utils import AUTH
from deciphon_api.errors import (
    FileNotInStorageError,
    ConflictError,
    HMMNotFoundError,
)
from deciphon_api.models import HMM, HMMIn, Job, JobType
from deciphon_api.sched import Sched, select

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


@router.post("/hmms/", response_model=HMM, status_code=CREATED, dependencies=AUTH)
async def create_hmm(hmm: HMMIn):
    if not storage_has(hmm.sha256):
        raise FileNotInStorageError(hmm.sha256)

    x = HMM(sha256=hmm.sha256, filename=hmm.filename, job=Job(type=JobType.hmm))

    with Sched() as sched:
        sched.add(x)
        try:
            sched.commit()
        except IntegrityError as e:
            raise ConflictError(str(e.orig))

        sched.refresh(x)
        return x


@router.get("/hmms/{hmm_id}", response_model=HMM, status_code=OK)
async def get_hmm(hmm_id: int = IDPath()):
    with Sched() as sched:
        hmm = sched.get(HMM, hmm_id)
        if not hmm:
            raise HMMNotFoundError()
        return hmm


@router.get("/hmms", response_model=List[HMM], status_code=OK)
async def list_hmms():
    with Sched() as sched:
        return sched.exec(select(HMM)).all()


@router.delete("/hmms/{hmm_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_hmm(hmm_id: int = IDPath()):
    with Sched() as sched:
        hmm = sched.get(HMM, hmm_id)
        if not hmm:
            raise HMMNotFoundError()
        sched.delete(hmm)
        sched.commit()
