import sqlalchemy.exc
from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import ID
from deciphon_api.auth import auth_request
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ConflictException, HMMNotFoundException
from deciphon_api.models import HMM, Job, JobType
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

AUTH = [Depends(auth_request)]
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED
BUFSIZE = 4 * 1024 * 1024


@router.delete("/hmms/{hmm_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def remove_hmm(hmm_id: int = ID()):
    with Session(get_sched()) as session:
        hmm = session.get(HMM, hmm_id)
        if not hmm:
            raise HMMNotFoundException()
        session.delete(hmm)
        session.commit()


def HMMFile():
    return File(content_type="text/plain", description="hmmer database")


@router.post("/hmms/", response_model=HMM, status_code=CREATED, dependencies=AUTH)
async def upload_hmm(hmm_file: UploadFile = HMMFile()):
    file = await get_depo().store_hmm(hmm_file)
    job = Job(type=JobType.hmm)
    hmm = HMM(xxh3=file.xxh3_64, filename=file.name, job=job)

    with Session(get_sched()) as session:
        session.add(hmm)
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise ConflictException(str(e.orig))
        session.refresh(hmm)
        return hmm
