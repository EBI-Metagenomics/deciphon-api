from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH
from deciphon_api.errors import FileNotInStorageError, NotFoundInSchedError
from deciphon_api.journal import get_journal
from deciphon_api.models import (
    DB,
    Job,
    JobType,
    ProdCreate,
    ProdRead,
    Scan,
    ScanCreate,
    ScanRead,
    Seq,
    SeqRead,
)
from deciphon_api.sched import Sched, select
from deciphon_api.storage import storage_has

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


@router.get("/scans", response_model=List[ScanRead], status_code=OK)
async def read_scans():
    with Sched() as sched:
        return [ScanRead.from_orm(x) for x in sched.exec(select(Scan)).all()]


@router.post("/scans/", response_model=ScanRead, status_code=CREATED)
async def create_scan(scan: ScanCreate):
    with Sched() as sched:
        if not sched.get(DB, scan.db_id):
            raise NotFoundInSchedError("DB")

        x = Scan.from_orm(scan)
        x.job = Job(type=JobType.scan)
        x.seqs = [Seq.from_orm(i) for i in scan.seqs]
        sched.add(x)
        sched.commit()
        sched.refresh(x)
        y = ScanRead.from_orm(x)
        await get_journal().publish_scan(y.id)
        return y


@router.get("/scans/{scan_id}", response_model=ScanRead, status_code=OK)
async def read_scan(scan_id: int):
    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        if not scan:
            raise NotFoundInSchedError("Scan")
        return ScanRead.from_orm(scan)


@router.delete("/scans/{scan_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_scan(scan_id: int):
    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        if not scan:
            raise NotFoundInSchedError("Scan")
        sched.delete(scan)
        sched.commit()


@router.get("/scans/{scan_id}/seqs", response_model=List[SeqRead], status_code=OK)
async def read_seqs(scan_id: int):
    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        if not scan:
            raise NotFoundInSchedError("Scan")
        return [SeqRead.from_orm(i) for i in scan.seqs]


@router.get("/scans/{scan_id}/prods", response_model=List[ProdRead], status_code=OK)
async def read_prods(scan_id: int):
    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        if not scan:
            raise NotFoundInSchedError("Scan")
        return [ProdRead.from_orm(i) for i in scan.prods]


@router.get("/scans/{scan_id}/prods", response_model=List[ProdRead], status_code=OK)
async def create_prods(scan_id: int, prods: ProdCreate):
    if not storage_has(prods.sha256):
        raise FileNotInStorageError(prods.sha256)

    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        if not scan:
            raise NotFoundInSchedError("Scan")
        # TODO: aqui
        return [ProdRead.from_orm(i) for i in scan.prods]
