from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH
from deciphon_api.errors import (
    FileNotInStorageError,
    NotFoundInSchedError,
)
from deciphon_api.models import (
    DB,
    HMM,
    DBCreate,
    DBRead,
)
from deciphon_api.sched import Sched, select
from deciphon_api.storage import storage_has

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


@router.get("/dbs", response_model=List[DBRead], status_code=OK)
async def read_dbs():
    with Sched() as sched:
        return [DBRead.from_orm(x) for x in sched.exec(select(DB)).all()]


@router.post("/dbs/", response_model=DBRead, status_code=CREATED, dependencies=AUTH)
async def create_db(db: DBCreate):
    if not storage_has(db.sha256):
        raise FileNotInStorageError(db.sha256)

    with Sched() as sched:
        stmt = select(HMM).where(HMM.filename == db.expected_hmm_filename)
        hmm = sched.exec(stmt).one_or_none()
        if not hmm:
            raise NotFoundInSchedError("HMM")

        hmm.job.set_done()

        x = DB.from_orm(db)
        x.hmm = hmm
        sched.add(x)
        sched.commit()
        sched.refresh(x)
        return DBRead.from_orm(x)


@router.get("/dbs/{db_id}", response_model=DBRead, status_code=OK)
async def read_db(db_id: int):
    with Sched() as sched:
        db = sched.get(DB, db_id)
        if not db:
            raise NotFoundInSchedError("DB")
        return DBRead.from_orm(db)


@router.delete("/dbs/{db_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_db(db_id: int):
    with Sched() as sched:
        db = sched.get(DB, db_id)
        if not db:
            raise NotFoundInSchedError("DB")
        sched.delete(db)
        sched.commit()
