from typing import List

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.responses import responses
from deciphon_api.csched import ffi, lib
from deciphon_api.errors import ConditionError, InternalError, NotFoundError
from deciphon_api.models.db import DB
from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan import Scan, ScanPost
from deciphon_api.models.seq import Seq
from deciphon_api.rc import RC

router = APIRouter()


@router.post(
    "/scans/",
    summary="submit scan job",
    response_model=Job,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="scans:submit-scan",
)
def submit_scan(scan: ScanPost = Body(..., example=ScanPost.example())):
    if not DB.exists_by_id(scan.db_id):
        raise NotFoundError("database")

    seqs = scan.seqs
    if len(seqs) > lib.NUM_SEQS_PER_JOB:
        raise ConditionError("too many sequences")

    scan_ptr = ffi.new("struct sched_scan *")
    lib.sched_scan_init(scan_ptr, scan.db_id, scan.multi_hits, scan.hmmer3_compat)

    for seq in scan.seqs:
        lib.sched_scan_add_seq(scan_ptr, seq.name.encode(), seq.data.encode())

    job_ptr = ffi.new("struct sched_job *")
    lib.sched_job_init(job_ptr, lib.SCHED_SCAN)
    rc = RC(lib.sched_job_submit(job_ptr, scan_ptr))
    assert rc != RC.END
    assert rc != RC.NOTFOUND

    if rc != RC.OK:
        raise InternalError(rc)

    return Job.from_cdata(job_ptr)


@router.get(
    "/scans/{scan_id}/seqs",
    summary="get sequences of scan",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-sequences-of-scan",
)
def get_sequences_of_scan(scan_id: int):
    return Scan.from_id(scan_id).seqs()


@router.get(
    "/scans/{scan_id}/seqs/next/{seq_id}",
    summary="get next sequence",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-next-sequence-of-scan",
)
def get_next_sequence_of_scan(scan_id: int, seq_id: int):
    ptr = ffi.new("struct sched_seq *")
    cscan = ptr[0]
    cscan.id = seq_id
    cscan.scan_id = scan_id
    rc = RC(lib.sched_seq_next(ptr))

    if rc == RC.END:
        return []

    if rc == RC.NOTFOUND:
        raise NotFoundError("scan")

    if rc != RC.OK:
        raise InternalError(rc)

    return [Seq.from_cdata(cscan)]


@router.get(
    "/scans/{scan_id}/prods",
    summary="get products of scan",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-products-of-scan",
)
def get_products_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()
    job.assert_state(JobState.done)
    return scan.prods()


@router.get(
    "/scans/{scan_id}/prods/gff",
    summary="get products of scan as gff",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-products-of-scan-as-gff",
)
def get_products_of_scan_as_gff(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()
    job.assert_state(JobState.done)
    return scan.result().gff()


@router.get(
    "/scans/{scan_id}/prods/hmm_paths",
    summary="get hmm paths of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-hmm-paths-of-scan",
)
def get_hmm_paths_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()
    job.assert_state(JobState.done)
    return scan.result().fasta("state")


@router.get(
    "/scans/{scan_id}/prods/fragments",
    summary="get fragments of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-fragments-of-scan",
)
def get_fragments_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()
    job.assert_state(JobState.done)
    return scan.result().fasta("frag")


@router.get(
    "/scans/{scan_id}/prods/codons",
    summary="get codons of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-codons-of-scan",
)
def get_codons_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()
    job.assert_state(JobState.done)
    return scan.result().fasta("codon")


@router.get(
    "/scans/{scan_id}/prods/aminos",
    summary="get aminos of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-aminos-of-scan",
)
def get_aminos_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()
    job.assert_state(JobState.done)
    return scan.result().fasta("amino")
