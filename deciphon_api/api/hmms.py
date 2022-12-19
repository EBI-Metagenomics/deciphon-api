import sqlalchemy.exc
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

import deciphon_api.mime as mime
from deciphon_api.api.files import HMMFile
from deciphon_api.api.utils import AUTH, ID
from deciphon_api.broker import broker_publish_hmm
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.models import HMM, Job, JobType
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


@router.get("/hmms/{hmm_id}", response_model=HMM, status_code=OK)
async def get_hmm_by_id(hmm_id: int = ID()):
    with Session(get_sched()) as session:
        hmm = session.get(HMM, hmm_id)
        if not hmm:
            raise NotFoundException(HMM)
        return hmm


@router.get("/hmms/xxh3/{xxh3}", response_model=HMM, status_code=OK)
async def get_hmm_by_xxh3(xxh3: int):
    with Session(get_sched()) as session:
        stmt = select(HMM).where(HMM.xxh3 == xxh3)
        hmm = session.exec(stmt).one_or_none()
        if not hmm:
            raise NotFoundException(HMM)
        return hmm


@router.get("/hmms/filename/{filename}", response_model=HMM, status_code=OK)
async def get_hmm_by_filename(filename: str):
    with Session(get_sched()) as session:
        stmt = select(HMM).where(HMM.filename == filename)
        hmm = session.exec(stmt).one_or_none()
        if not hmm:
            raise NotFoundException(HMM)
        return hmm


@router.get("/hmms", response_model=list[HMM], status_code=OK)
async def get_all_hmms():
    with Session(get_sched()) as session:
        return session.exec(select(HMM)).all()


@router.get("/hmms/{hmm_id}/download", response_class=FileResponse, status_code=OK)
async def download_hmm(hmm_id: int = ID()):
    with Session(get_sched()) as session:
        hmm = session.get(HMM, hmm_id)
        if not hmm:
            raise NotFoundException(HMM)
        file = get_depo().fetch(hmm)
        media_type = mime.TEXT
        return FileResponse(file.path, media_type=media_type, filename=file.name)


@router.delete("/hmms/{hmm_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_hmm(hmm_id: int = ID()):
    with Session(get_sched()) as session:
        hmm = session.get(HMM, hmm_id)
        if not hmm:
            raise NotFoundException(HMM)
        session.delete(hmm)
        session.commit()


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

        broker_publish_hmm(hmm.id, hmm.filename, hmm.job.id)
        return hmm
