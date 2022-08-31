from typing import List

import aiofiles
from fasta_reader import read_fasta
from fastapi import APIRouter, File, Form, Path, Query, UploadFile
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.responses import responses
from deciphon_api.models.count import Count
from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan import Scan, ScanConfig, ScanIDType, ScanPost
from deciphon_api.models.seq import Seq, SeqPost

router = APIRouter()


@router.get(
    "/scans/{id}",
    summary="get scan",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-scan",
    deprecated=True,
)
async def get_scan(
    id: int = Path(...), id_type: ScanIDType = Query(ScanIDType.SCAN_ID.value)
):
    return Scan.get(id, id_type)


@router.get(
    "/scans/{id}",
    summary="get scan by id",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-scan-by-id",
)
async def get_scan_by_id(id: int = Path(..., gt=0)):
    return Scan.get(id, ScanIDType.SCAN_ID)


@router.get(
    "/scans/job-id/{job_id}",
    summary="get scan by job_id",
    response_model=Scan,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-scan-by-job-id",
)
async def get_scan_by_job_id(job_id: int = Path(..., gt=0)):
    return Scan.get(job_id, ScanIDType.JOB_ID)


@router.post(
    "/scans/",
    summary="submit scan job",
    response_model=Job,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="scans:submit-scan",
)
async def submit_scan(
    db_id: int = Form(...),
    multi_hits: bool = Form(False),
    hmmer3_compat: bool = Form(False),
    fasta_file: UploadFile = File(
        ..., content_type="text/plain", description="fasta file"
    ),
):
    cfg = ScanConfig(db_id=db_id, multi_hits=multi_hits, hmmer3_compat=hmmer3_compat)
    scan = ScanPost(config=cfg)

    async with aiofiles.tempfile.NamedTemporaryFile("wb") as file:
        while content := await fasta_file.read(4 * 1024 * 1024):
            await file.write(content)
        assert not isinstance(file.name, int)
        await file.flush()
        for item in read_fasta(file.name):
            scan.seqs.append(SeqPost(name=item.id, data=item.sequence))

    return scan.submit()


@router.get(
    "/scans/{id}/seqs",
    summary="get sequences of scan",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-sequences-of-scan",
)
async def get_sequences_of_scan(id: int = Path(..., gt=0)):
    return Scan.get(id, ScanIDType.SCAN_ID).seqs()


@router.get(
    "/scans/{id}/seqs/count",
    summary="get sequence count of scan",
    response_model=Count,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-sequence-count-of-scan",
)
async def get_sequence_count_of_scan(id: int = Path(..., gt=0)):
    return Count(count=len(Scan.get(id, ScanIDType.SCAN_ID).seqs()))


@router.get(
    "/scans",
    summary="get scan list",
    response_model=List[Scan],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-scan-list",
)
async def get_scan_list():
    return Scan.get_list()


@router.get(
    "/scans/{id}/seqs/next/{seq_id}",
    summary="get next sequence",
    response_model=Seq,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-next-sequence-of-scan",
)
async def get_next_sequence_of_scan(
    id: int = Path(..., gt=0), seq_id: int = Path(..., ge=0)
):
    return Seq.next(seq_id, id)


@router.get(
    "/scans/{id}/prods",
    summary="get products of scan",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-products-of-scan",
)
async def get_products_of_scan(id: int = Path(..., gt=0)):
    scan = Scan.get(id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.prods()


@router.get(
    "/scans/{id}/prods/gff",
    summary="get products of scan as gff",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-products-of-scan-as-gff",
)
async def get_products_of_scan_as_gff(id: int = Path(..., gt=0)):
    scan = Scan.get(id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().gff()


@router.get(
    "/scans/{id}/prods/path",
    summary="get hmm paths of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-path-of-scan",
)
async def get_path_of_scan(id: int = Path(..., gt=0)):
    scan = Scan.get(id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("state")


@router.get(
    "/scans/{id}/prods/fragment",
    summary="get fragments of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-fragments-of-scan",
)
async def get_fragment_of_scan(id: int = Path(..., gt=0)):
    scan = Scan.get(id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("frag")


@router.get(
    "/scans/{id}/prods/codon",
    summary="get codons of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-codons-of-scan",
)
async def get_codons_of_scan(id: int = Path(..., gt=0)):
    scan = Scan.get(id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("codon")


@router.get(
    "/scans/{id}/prods/amino",
    summary="get aminos of scan",
    response_class=PlainTextResponse,
    status_code=HTTP_200_OK,
    responses=responses,
    name="scans:get-aminos-of-scan",
)
async def get_aminos_of_scan(id: int = Path(..., gt=0)):
    scan = Scan.get(id, ScanIDType.SCAN_ID)
    job = scan.job()
    job.assert_state(JobState.SCHED_DONE)
    return scan.result().fasta("amino")
