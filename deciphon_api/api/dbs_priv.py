import sqlalchemy.exc
from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session, select
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import ID
from deciphon_api.auth import auth_request
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import (
    ConflictException,
    DBNotFoundException,
    HMMNotFoundException,
)
from deciphon_api.models import DB, HMM
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

AUTH = [Depends(auth_request)]
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED
BUFSIZE = 4 * 1024 * 1024


@router.delete("/dbs/{db_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def remove_db(db_id: int = ID()):
    with Session(get_sched()) as session:
        db = session.get(DB, db_id)
        if not db:
            raise DBNotFoundException()
        session.delete(db)
        session.commit()


def DBFile():
    content_type = "application/octet-stream"
    return File(content_type=content_type, description="deciphon database")


@router.post("/dbs/", response_model=DB, status_code=CREATED, dependencies=AUTH)
async def upload_db(db_file: UploadFile = DBFile()):

    hmm_filename = db_file.filename.replace(".dcp", ".hmm")
    with Session(get_sched()) as session:
        stmt = select(HMM).where(HMM.filename == hmm_filename)
        hmm = session.exec(stmt).one_or_none()
        if not hmm:
            raise HMMNotFoundException()

    file = await get_depo().store_db(db_file)
    db = DB(xxh3=file.xxh3_64, filename=file.name, hmm=hmm)

    with Session(get_sched()) as session:
        session.add(db)
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise ConflictException(str(e.orig))
        session.refresh(db)
        return db
