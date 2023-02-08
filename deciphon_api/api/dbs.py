from datetime import datetime

import sqlalchemy.exc
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

import deciphon_api.mime as mime
from deciphon_api.api.files import DBFile
from deciphon_api.api.utils import AUTH, ID
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.models import DB, HMM, JobState
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


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


@router.delete("/dbs/{db_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_db(db_id: int = ID()):
    with Session(get_sched()) as session:
        db = session.get(DB, db_id)
        if not db:
            raise NotFoundException(DB)
        session.delete(db)
        session.commit()


@router.post("/dbs/", response_model=DB, status_code=CREATED, dependencies=AUTH)
async def upload_db(db_file: UploadFile = DBFile()):
    hmm_filename = db_file.filename.replace(".dcp", ".hmm")
    file = await get_depo().store_db(db_file)

    with Session(get_sched()) as session:
        stmt = select(HMM).where(HMM.filename == hmm_filename)
        hmm = session.exec(stmt).one_or_none()
        if not hmm:
            raise NotFoundException(HMM)

        hmm.job.state = JobState.done
        hmm.job.progress = 100
        now = datetime.now()
        if not hmm.job.exec_started:
            hmm.job.exec_started = now
        hmm.job.exec_ended = now

        db = DB(xxh3=file.xxh3_64, filename=file.name, hmm=hmm)
        session.add(db)
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise ConflictException(str(e.orig))
        session.refresh(db)
        return db
