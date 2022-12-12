import sqlalchemy.exc
from fastapi import APIRouter, UploadFile
from sqlmodel import Session, select
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.files import DBFile
from deciphon_api.api.utils import AUTH, ID
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.models import DB, HMM, JobState
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


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
        db = DB(xxh3=file.xxh3_64, filename=file.name, hmm=hmm)
        session.add(db)
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise ConflictException(str(e.orig))
        session.refresh(db)
        return db
