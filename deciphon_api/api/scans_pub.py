import tempfile

from fasta_reader import read_fasta
from fastapi import APIRouter, File, Form, Path, UploadFile
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, col, select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api import mime
from deciphon_api.api.utils import ID
from deciphon_api.exceptions import (
    DBNotFoundException,
    ScanNotFoundException,
    SeqNotFoundException,
)
from deciphon_api.models import DB, Job, JobType, Scan, Seq
from deciphon_api.scan_result import ScanResult
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
CREATED = HTTP_201_CREATED
BUFSIZE = 4 * 1024 * 1024


def FastaFile():
    return File(content_type=mime.TEXT, description="fasta file")


@router.post("/scans/", response_model=Job, status_code=CREATED)
async def submit_scan(
    db_id: int = Form(...),
    multi_hits: bool = Form(False),
    hmmer3_compat: bool = Form(False),
    fasta_file: UploadFile = FastaFile(),
):
    job = Job(type=JobType.scan)
    scan = Scan(
        db_id=db_id, multi_hits=multi_hits, hmmer3_compat=hmmer3_compat, job=job
    )

    with tempfile.NamedTemporaryFile("wb") as file:
        while content := await fasta_file.read(BUFSIZE):
            file.write(content)
        file.flush()
        for item in read_fasta(file.name):
            scan.seqs.append(Seq(name=item.id, data=item.sequence))

    with Session(get_sched()) as session:
        db = session.get(DB, scan.db_id)
        if not db:
            raise DBNotFoundException()
        session.add(scan)
        session.commit()
        session.refresh(scan)
        return scan.job


@router.get("/scans/{scan_id}", response_model=Scan, status_code=OK)
async def get_scan_by_id(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise ScanNotFoundException()
        return scan


@router.get("/scans", response_model=list[Scan], status_code=OK)
async def get_scan_list():
    with Session(get_sched()) as session:
        return session.exec(select(Scan)).all()


@router.get("/scans/{scan_id}/seqs/next/{seq_id}", response_model=Seq, status_code=OK)
async def next_scan_seq(scan_id: int = ID(), seq_id: int = Path(...)):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise ScanNotFoundException()
        stmt = select(Seq).where(Seq.scan_id == scan_id, col(Seq.id) > seq_id)
        seq = session.exec(stmt).first()
        if not seq:
            raise SeqNotFoundException()
        return seq


@router.get("/scans/{scan_id}/seqs", response_model=list[Seq], status_code=OK)
async def get_scan_seq_list(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise ScanNotFoundException()
        return session.exec(select(Seq).where(Seq.scan_id == scan.id)).all()


@router.get(
    "/scans/{scan_id}/prods/gff", response_class=PlainTextResponse, status_code=OK
)
async def get_prod_as_gff(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise ScanNotFoundException()
        scan_result = ScanResult(scan)
        return scan_result.gff()
