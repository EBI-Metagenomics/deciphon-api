from fastapi import APIRouter
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK

from deciphon_api import mime
from deciphon_api.api.utils import ID
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import NotFoundException
from deciphon_api.models import HMM
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK


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
async def get_hmms():
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
