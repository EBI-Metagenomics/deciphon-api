from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH
from deciphon_api.errors import (
    FileNotInStorageError,
    NotFoundInDBError,
)
from deciphon_api.models import HMM, HMMCreate, HMMRead, Job, JobType
from deciphon_api.sched import Sched, select
from deciphon_api.storage import storage_has

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


@router.get("/hmms", response_model=List[HMMRead], status_code=OK)
async def read_hmms():
    with Sched() as sched:
        return [HMMRead.parse_obj(x) for x in sched.exec(select(HMM)).all()]


@router.post("/hmms/", response_model=HMMRead, status_code=CREATED, dependencies=AUTH)
async def create_hmm(hmm: HMMCreate):
    if not storage_has(hmm.sha256):
        raise FileNotInStorageError(hmm.sha256)

    with Sched() as sched:
        x = HMM.from_orm(hmm)
        x.job = Job(type=JobType.hmm)
        sched.add(x)
        sched.commit()
        sched.refresh(x)
        return HMMRead.parse_obj(x)


@router.get("/hmms/{hmm_id}", response_model=HMMRead, status_code=OK)
async def read_hmm(hmm_id: int):
    with Sched() as sched:
        hmm = sched.get(HMM, hmm_id)
        if not hmm:
            raise NotFoundInDBError("HMM")
        return hmm


@router.delete("/hmms/{hmm_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_hmm(hmm_id: int):
    with Sched() as sched:
        hmm = sched.get(HMM, hmm_id)
        if not hmm:
            raise NotFoundInDBError("HMM")
        sched.delete(hmm)
        sched.commit()
