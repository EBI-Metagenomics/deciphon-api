from fastapi import APIRouter
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK

from deciphon_api import mime
from deciphon_api.api.utils import ID
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import NotFoundException
from deciphon_api.models import DB
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK


@router.get("/dbs/{db_id}", response_model=DB, status_code=OK)
async def get_db_by_id(db_id: int = ID()):
    with Session(get_sched()) as session:
        db = session.get(DB, db_id)
        if not db:
            raise NotFoundException(DB)
        return db


@router.get("/dbs/xxh3/{xxh3}", response_model=DB, status_code=OK)
async def get_db_by_xxh3(xxh3: int):
    with Session(get_sched()) as session:
        stmt = select(DB).where(DB.xxh3 == xxh3)
        db = session.exec(stmt).one_or_none()
        if not db:
            raise NotFoundException(DB)
        return db


@router.get("/dbs/filename/{filename}", response_model=DB, status_code=OK)
async def get_db_by_filename(filename: str):
    with Session(get_sched()) as session:
        stmt = select(DB).where(DB.filename == filename)
        db = session.exec(stmt).one_or_none()
        if not db:
            raise NotFoundException(DB)
        return db


@router.get("/dbs", response_model=list[DB], status_code=OK)
async def get_dbs():
    with Session(get_sched()) as session:
        return session.exec(select(DB)).all()


@router.get("/dbs/{db_id}/download", response_class=FileResponse, status_code=OK)
async def download_db(db_id: int = ID()):
    with Session(get_sched()) as session:
        db = session.get(DB, db_id)
        if not db:
            raise NotFoundException(DB)
        file = get_depo().fetch(db)
        media_type = mime.OCTET
        return FileResponse(file.path, media_type=media_type, filename=file.name)
