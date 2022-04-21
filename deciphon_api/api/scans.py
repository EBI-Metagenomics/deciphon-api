from typing import List

from fastapi import APIRouter, Body, Path, Query
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.responses import responses
from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan import Scan, ScanIDType, ScanPost
from deciphon_api.models.seq import Seq

router = APIRouter()


@router.get(
    "/scans/{id}",
    summary="get hmm",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-scan",
)
def get_scan(
    id: int = Path(...), id_type: ScanIDType = Query(ScanIDType.SCAN_ID.value)
):
    return Scan.get(id, id_type)


@router.post(
    "/scans/",
    summary="submit scan job",
    response_model=Job,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="scans:submit-scan",
)
def submit_scan(scan: ScanPost = Body(..., example=ScanPost.example())):
    return scan.submit()


@router.get(
    "/scans/{scan_id}/seqs",
    summary="get sequences of scan",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-sequences-of-scan",
)
def get_sequences_of_scan(scan_id: int = Path(..., gt=0)):
    return Scan.get(scan_id, ScanIDType.SCAN_ID).seqs()


@router.get(
    "/scans",
    summary="get scan list",
    response_model=List[Scan],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-scan-list",
)
def get_scan_list():
    return Scan.get_list()


@router.get(
    "/scans/{scan_id}/seqs/next/{seq_id}",
    summary="get next sequence",
    response_model=Seq,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-next-sequence-of-scan",
)
def get_next_sequence_of_scan(
    scan_id: int = Path(..., gt=0), seq_id: int = Path(..., ge=0)
):
    return Seq.next(seq_id, scan_id)


@router.get(
    "/scans/{scan_id}/prods",
    summary="get products of scan",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-products-of-scan",
)
def get_products_of_scan(scan_id: int = Path(..., gt=0)):
    scan = Scan.get(scan_id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.prods()


@router.get(
    "/scans/{scan_id}/prods/gff",
    summary="get products of scan as gff",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-products-of-scan-as-gff",
)
def get_products_of_scan_as_gff(scan_id: int = Path(..., gt=0)):
    scan = Scan.get(scan_id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().gff()


@router.get(
    "/scans/{scan_id}/prods/path",
    summary="get hmm paths of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-path-of-scan",
)
def get_path_of_scan(scan_id: int = Path(..., gt=0)):
    scan = Scan.get(scan_id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("state")


@router.get(
    "/scans/{scan_id}/prods/fragment",
    summary="get fragments of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-fragments-of-scan",
)
def get_fragment_of_scan(scan_id: int = Path(..., gt=0)):
    scan = Scan.get(scan_id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("frag")


@router.get(
    "/scans/{scan_id}/prods/codon",
    summary="get codons of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-codons-of-scan",
)
def get_codons_of_scan(scan_id: int = Path(..., gt=0)):
    scan = Scan.get(scan_id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("codon")


@router.get(
    "/scans/{scan_id}/prods/amino",
    summary="get aminos of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-aminos-of-scan",
)
def get_aminos_of_scan(scan_id: int = Path(..., gt=0)):
    scan = Scan.get(scan_id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("amino")
