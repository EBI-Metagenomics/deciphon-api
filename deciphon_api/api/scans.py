from typing import List

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api._types import ErrorResponse
from deciphon_api.csched import ffi, lib
from deciphon_api.exception import EINVALException, create_exception
from deciphon_api.models.db import DB
from deciphon_api.models.job import JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan import Scan, ScanPost
from deciphon_api.models.seq import Seq
from deciphon_api.rc import RC

router = APIRouter()


# @router.post(
#     "/scans/",
#     summary="add scan",
#     response_model=Scan,
#     status_code=HTTP_201_CREATED,
#     responses={
#         HTTP_404_NOT_FOUND: {"model": ErrorResponse},
#         HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
#     },
# )
# def add_scan(scan: ScanPost = Body(..., example=ScanPost.example())):
#     if not DB.exists_by_id(scan.db_id):
#         raise EINVALException(HTTP_404_NOT_FOUND, "database not found")
#
#     cjob = ffi.new("struct sched_job *")
#     cjob[0].id = 0
#     cjob[0].db_id = scan.db_id
#     cjob[0].multi_hits = scan.multi_hits
#     cjob[0].hmmer3_compat = scan.hmmer3_compat
#
#     # TODO: implement try-catch all to call sched_job_rollback_submission
#     # in case of cancel/failure.
#     rc = RC(lib.sched_job_begin_submission(cjob))
#     assert rc != RC.END
#     assert rc != RC.NOTFOUND
#
#     if rc != RC.OK:
#         raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)
#
#     for seq in scan.seqs:
#         lib.sched_job_add_seq(cjob, seq.name.encode(), seq.data.encode())
#
#     rc = RC(lib.sched_job_end_submission(cjob))
#     if rc != RC.OK:
#         raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)
#
#     return Scan.from_cdata(cjob)


@router.get(
    "/scans/{scan_id}/seqs",
    summary="get sequences of scan",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-sequences-of-scan",
)
def get_sequences_of_scan(scan_id: int):
    return Scan.from_id(scan_id).seqs()


@router.get(
    "/scans/{scan_id}/seqs/next/{seq_id}",
    summary="get next sequence",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
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
        raise EINVALException(HTTP_404_NOT_FOUND, "scan not found")

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return [Seq.from_cdata(cscan)]


@router.get(
    "/scans/{scan_id}/prods",
    summary="get products of scan",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-products-of-scan",
)
def get_products_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return scan.prods()


@router.get(
    "/scans/{scan_id}/prods/gff",
    summary="get products of scan as gff",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-products-of-scan-as-gff",
)
def get_products_of_scan_as_gff(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return scan.result().gff()


@router.get(
    "/scans/{scan_id}/prods/hmm_paths",
    summary="get hmm paths of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-hmm-paths-of-scan",
)
def get_hmm_paths_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return scan.result().fasta("state")


@router.get(
    "/scans/{scan_id}/prods/fragments",
    summary="get fragments of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-fragments-of-scan",
)
def get_fragments_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return scan.result().fasta("frag")


@router.get(
    "/scans/{scan_id}/prods/codons",
    summary="get codons of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-codons-of-scan",
)
def get_codons_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return scan.result().fasta("codon")


@router.get(
    "/scans/{scan_id}/prods/aminos",
    summary="get aminos of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_412_PRECONDITION_FAILED: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="scans:get-aminos-of-scan",
)
def get_aminos_of_scan(scan_id: int):
    scan = Scan.from_id(scan_id)
    job = scan.job()

    if job.state != JobState.done:
        raise EINVALException(HTTP_412_PRECONDITION_FAILED, "job is not in done state")

    return scan.result().fasta("amino")
