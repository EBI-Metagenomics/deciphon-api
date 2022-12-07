import tempfile

from fasta_reader import read_fasta
from fastapi import APIRouter, Form, Path, UploadFile
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, col, select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.files import FastaFile
from deciphon_api.api.utils import ID
from deciphon_api.bufsize import BUFSIZE
from deciphon_api.exceptions import NotFoundException
from deciphon_api.models import DB, Job, JobType, Scan, Seq
from deciphon_api.scan_result import ScanResult
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
CREATED = HTTP_201_CREATED
PLAIN = PlainTextResponse


@router.post("/scans/", response_model=Job, status_code=CREATED)
async def upload_scan(
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
            raise NotFoundException(DB)
        session.add(scan)
        session.commit()
        session.refresh(scan)
        return scan.job


@router.get("/scans/{scan_id}", response_model=Scan, status_code=OK)
async def get_scan_by_id(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        return scan


@router.get("/scans", response_model=list[Scan], status_code=OK)
async def get_scans():
    with Session(get_sched()) as session:
        return session.exec(select(Scan)).all()


@router.get("/scans/{scan_id}/seqs/next/{seq_id}", response_model=Seq, status_code=OK)
async def get_next_scan_seq(scan_id: int = ID(), seq_id: int = Path(...)):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        stmt = select(Seq).where(Seq.scan_id == scan_id, col(Seq.id) > seq_id)
        seq = session.exec(stmt).first()
        if not seq:
            raise NotFoundException(Seq)
        return seq


@router.get("/scans/{scan_id}/seqs", response_model=list[Seq], status_code=OK)
async def get_scan_seqs(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        return session.exec(select(Seq).where(Seq.scan_id == scan.id)).all()


@router.get("/scans/{scan_id}/prods/gff", response_class=PLAIN, status_code=OK)
async def get_prod_gff(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.gff()


@router.get("/scans/{scan_id}/prods/amino", response_class=PLAIN, status_code=OK)
async def get_prod_amino(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.fasta("amino")


@router.get("/scans/{scan_id}/prods/codon", response_class=PLAIN, status_code=OK)
async def get_prod_codon(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.fasta("codon")


@router.get("/scans/{scan_id}/prods/frag", response_class=PLAIN, status_code=OK)
async def get_prod_frag(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.fasta("frag")


@router.get("/scans/{scan_id}/prods/path", response_class=PLAIN, status_code=OK)
async def get_prod_path(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.fasta("state")
