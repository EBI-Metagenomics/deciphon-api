import tempfile
import textwrap
from datetime import datetime

import sqlalchemy.exc
from fasta_reader import read_fasta
from fastapi import APIRouter, Depends, Form, Path, UploadFile
from fastapi.responses import PlainTextResponse
from kombu import Connection, Exchange, Queue
from sqlmodel import Session, col, select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.files import FastaFile, ProdFile
from deciphon_api.api.utils import AUTH, ID
from deciphon_api.bufsize import BUFSIZE
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.hmmer_result import HMMERResult
from deciphon_api.models import DB, Job, JobState, JobType, Prod, Scan, Seq
from deciphon_api.prodfile import ProdFileReader
from deciphon_api.scan_result import ScanResult
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
CREATED = HTTP_201_CREATED
PLAIN = PlainTextResponse


def get_session():
    with Session(get_sched()) as session:
        yield session


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

        exchange = Exchange("scan", "direct", durable=True)
        queue = Queue("scan", exchange=exchange, routing_key="scan")

        with Connection("amqp://guest:guest@localhost//") as conn:
            producer = conn.Producer(serializer="json")
            producer.publish(
                {
                    "id": scan.id,
                    "hmm_id": db.hmm.id,
                    "hmm_file": db.hmm.filename,
                    "db_id": db_id,
                    "db_file": db.filename,
                    "job_id": scan.job.id,
                },
                exchange=exchange,
                routing_key="scan",
                declare=[queue],
            )

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


@router.get("/scans/{scan_id}/prods", response_model=list[Prod], status_code=OK)
async def get_scan_prods(
    scan_id: int = ID(),
    session: Session = Depends(get_session),
):
    scan = session.get(Scan, scan_id)
    if not scan:
        raise NotFoundException(Scan)
    return scan.prods


def get_hmmer_result(scan, prod_id: int):
    if not scan:
        raise NotFoundException(Scan)
    for prod in scan.prods:
        if prod.id == prod_id:
            depo = get_depo()
            return HMMERResult(depo.fetch_blob(prod.hmmer_sha256))
    else:
        raise NotFoundException(Prod)


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/hmmer/targets",
    response_class=PLAIN,
    status_code=OK,
)
async def get_hmmer_targets(
    scan_id: int = ID(),
    prod_id: int = ID(),
    session: Session = Depends(get_session),
):
    return get_hmmer_result(session.get(Scan, scan_id), prod_id).targets()


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/hmmer/domains",
    response_class=PLAIN,
    status_code=OK,
)
async def get_hmmer_domains(
    scan_id: int = ID(),
    prod_id: int = ID(),
    session: Session = Depends(get_session),
):
    return get_hmmer_result(session.get(Scan, scan_id), prod_id).domains()


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/hmmer/targets-table",
    response_class=PLAIN,
    status_code=OK,
)
async def get_hmmer_targets_table(
    scan_id: int = ID(),
    prod_id: int = ID(),
    session: Session = Depends(get_session),
):
    return get_hmmer_result(session.get(Scan, scan_id), prod_id).targets_table()


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/hmmer/domains-table",
    response_class=PLAIN,
    status_code=OK,
)
async def get_hmmer_domains_table(
    scan_id: int = ID(),
    prod_id: int = ID(),
    session: Session = Depends(get_session),
):
    return get_hmmer_result(session.get(Scan, scan_id), prod_id).domains_table()


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


@router.get("/scans/{scan_id}/prods/query", response_class=PLAIN, status_code=OK)
async def get_prod_query(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.fasta("query")


@router.get("/scans/{scan_id}/prods/path", response_class=PLAIN, status_code=OK)
async def get_prod_path(scan_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        return scan_result.fasta("state")


# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/query/{idx}",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_query_stream(
#     scan_id: int = ID(), prod_id: int = ID(), idx: int = IDX()
# ):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).query_stream(idx)
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/state/{idx}",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_state_stream(
#     scan_id: int = ID(), prod_id: int = ID(), idx: int = IDX()
# ):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).state_stream(idx)
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/codon/{idx}",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_codon_stream(
#     scan_id: int = ID(), prod_id: int = ID(), idx: int = IDX()
# ):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).codon_stream(idx)
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/amino/{idx}",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_amino_stream(
#     scan_id: int = ID(), prod_id: int = ID(), idx: int = IDX()
# ):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).amino_stream(idx)
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/hmmer/hmm-cs",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_hmmer_cs_stream(scan_id: int = ID(), prod_id: int = ID()):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).hmmer().hmm_cs_stream()
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/hmmer/seq-cs",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_seq_cs_stream(scan_id: int = ID(), prod_id: int = ID()):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).hmmer().seq_cs_stream()
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/hmmer/match",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_match_stream(scan_id: int = ID(), prod_id: int = ID()):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).hmmer().match_stream()
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/hmmer/target",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_target_stream(scan_id: int = ID(), prod_id: int = ID()):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         prod = scan.get_prod(prod_id)
#         hit_bounds = prod.hit_bounds()
#         start = hit_bounds[0][0]
#         print(start)
#         return " " * start + prod.hmmer().target_stream()
#
#
# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/streams/hmmer/pp",
#     response_class=PLAIN,
#     status_code=OK,
# )
# async def get_prod_pp_stream(scan_id: int = ID(), prod_id: int = ID()):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).hmmer().pp_stream()


# @router.get(
#     "/scans/{scan_id}/prods/{prod_id}/hits", response_model=list[Hit], status_code=OK
# )
# async def get_prod_hits(scan_id: int = ID(), prod_id: int = ID()):
#     with Session(get_sched()) as session:
#         scan = session.get(Scan, scan_id)
#         if not scan:
#             raise NotFoundException(Scan)
#         return scan.get_prod(prod_id).hits


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/fpath", response_class=PLAIN, status_code=OK
)
async def get_prod_fpath(scan_id: int = ID(), prod_id: int = ID()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        scan_result = ScanResult(scan)
        (
            state_stream,
            amino_stream,
            codon1_stream,
            codon2_stream,
            codon3_stream,
            query1_stream,
            query2_stream,
            query3_stream,
            query4_stream,
            query5_stream,
        ) = scan_result.path(scan_result.get_prod(prod_id))
        (
            hmm_cs_stream,
            seq_cs_stream,
            match_stream,
            target_stream,
            pp_stream,
        ) = get_hmmer_result(scan, prod_id).stream()

        hmm_cs_stream = "  " + hmm_cs_stream + "  "
        seq_cs_stream = "  " + seq_cs_stream + "  "
        match_stream = "  " + match_stream + "  "
        target_stream = "  " + target_stream + "  "
        pp_stream = "  " + pp_stream + "  "

        kwargs = {"drop_whitespace": False, "break_on_hyphens": False}
        states = textwrap.wrap(state_stream, 99, **kwargs)
        aminos = textwrap.wrap(amino_stream, 99, **kwargs)
        codon1 = textwrap.wrap(codon1_stream, 99, **kwargs)
        codon2 = textwrap.wrap(codon2_stream, 99, **kwargs)
        codon3 = textwrap.wrap(codon3_stream, 99, **kwargs)
        querys1 = textwrap.wrap(query1_stream, 99, **kwargs)
        querys2 = textwrap.wrap(query2_stream, 99, **kwargs)
        querys3 = textwrap.wrap(query3_stream, 99, **kwargs)
        querys4 = textwrap.wrap(query4_stream, 99, **kwargs)
        querys5 = textwrap.wrap(query5_stream, 99, **kwargs)
        hmm_cs = textwrap.wrap(hmm_cs_stream, 99, **kwargs)
        seq_cs = textwrap.wrap(seq_cs_stream, 99, **kwargs)
        match = textwrap.wrap(match_stream, 99, **kwargs)
        target = textwrap.wrap(target_stream, 99, **kwargs)
        pp = textwrap.wrap(pp_stream, 99, **kwargs)

        content = ""
        for r0, r1, c1, c2, c3, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11 in zip(
            states,
            aminos,
            codon1,
            codon2,
            codon3,
            querys1,
            querys2,
            querys3,
            querys4,
            querys5,
            hmm_cs,
            seq_cs,
            match,
            target,
            pp,
        ):
            content += "state  " + r0 + "\n"
            content += "amino  " + r1 + "\n"
            content += "codon  " + c1 + "\n"
            content += "       " + c2 + "\n"
            content += "       " + c3 + "\n"
            content += "seq    " + r2 + "\n"
            content += "       " + r3 + "\n"
            content += "       " + r4 + "\n"
            content += "       " + r5 + "\n"
            content += "       " + r6 + "\n"
            content += "CS     " + r7 + "\n"
            content += "ACC    " + r8 + "\n"
            content += "MATCH  " + r9 + "\n"
            content += "TARGET " + r10 + "\n"
            content += "PP     " + r11 + "\n"
            content += "\n"

        return content


@router.post(
    "/scans/{scan_id}/prods/",
    response_model=list[Prod],
    status_code=CREATED,
    dependencies=AUTH,
)
async def upload_prod(
    scan_id: int = ID(),
    prod_file: UploadFile = ProdFile(),
    session: Session = Depends(get_session),
):

    with tempfile.NamedTemporaryFile("wb") as file:
        while content := await prod_file.read(BUFSIZE):
            file.write(content)
        file.flush()

        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)

        scan.job.state = JobState.done
        scan.job.progress = 100
        scan.job.exec_ended = datetime.now()

        prod_reader = ProdFileReader(file.name)
        match_file = prod_reader.match_file()
        for match in match_file.read_records():
            assert match.scan_id == scan_id
            hmmer_blob = prod_reader.hmmer_blob(match.seq_id, match.profile)
            assert hmmer_blob is not None
            depo = get_depo()
            sha256_hexdigest = await depo.store_blob(hmmer_blob)
            prod = Prod(**match.dict(), hmmer_sha256=sha256_hexdigest)
            scan.prods.append(prod)
            session.add(prod)
            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                raise ConflictException(str(e.orig))
        session.refresh(scan)
        return scan.prods
