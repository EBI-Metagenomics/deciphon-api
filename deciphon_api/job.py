from enum import Enum
import os
from typing import List

from fastapi import Body, File, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from . import examples
from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .prod import Prod, create_prod
from .prod import ProdIn, get_prod, prod_in_example
from .rc import Code, RC, ReturnData
from .seq import Seq


class JobState(str, Enum):
    pend = "pend"
    run = "run"
    done = "done"
    fail = "fail"


class Job(BaseModel):
    id: int = 0

    db_id: int = 0
    multi_hits: bool = False
    hmmer3_compat: bool = False
    state: JobState = JobState.pend

    error: str = ""
    submission: int = 0
    exec_started: int = 0
    exec_ended: int = 0

    @classmethod
    def from_cdata(cls, cjob):
        return cls(
            id=int(cjob[0].id),
            db_id=int(cjob[0].db_id),
            multi_hits=bool(cjob[0].multi_hits),
            hmmer3_compat=bool(cjob[0].hmmer3_compat),
            state=ffi.string(cjob[0].state).decode(),
            error=ffi.string(cjob[0].error).decode(),
            submission=int(cjob[0].submission),
            exec_started=int(cjob[0].exec_started),
            exec_ended=int(cjob[0].exec_ended),
        )


class SeqIn(BaseModel):
    name: str = ""
    data: str = ""


class JobIn(BaseModel):
    db_id: int = 0
    multi_hits: bool = False
    hmmer3_compat: bool = False
    seqs: List[SeqIn] = []


job_in_example = JobIn(
    db_id=1,
    multi_hits=True,
    hmmer3_compat=False,
    seqs=[
        SeqIn(
            name="Homoserine_dh-consensus",
            data="CCTATCATTTCGACGCTCAAGGAGTCGCTGACAGGTGACCGTATTACTCGAATCGAAGGG"
            "ATATTAAACGGCACCCTGAATTACATTCTCACTGAGATGGAGGAAGAGGGGGCTTCATTC"
            "TCTGAGGCGCTGAAGGAGGCACAGGAATTGGGCTACGCGGAAGCGGATCCTACGGACGAT"
            "GTGGAAGGGCTAGATGCTGCTAGAAAGCTGGCAATTCTAGCCAGATTGGCATTTGGGTTA"
            "GAGGTCGAGTTGGAGGACGTAGAGGTGGAAGGAATTGAAAAGCTGACTGCCGAAGATATT"
            "GAAGAAGCGAAGGAAGAGGGTAAAGTTTTAAAACTAGTGGCAAGCGCCGTCGAAGCCAGG"
            "GTCAAGCCTGAGCTGGTACCTAAGTCACATCCATTAGCCTCGGTAAAAGGCTCTGACAAC"
            "GCCGTGGCTGTAGAAACGGAACGGGTAGGCGAACTCGTAGTGCAGGGACCAGGGGCTGGC"
            "GCAGAGCCAACCGCATCCGCTGTACTCGCTGACCTTCTC",
        ),
        SeqIn(
            name="AA_kinase-consensus",
            data="AAACGTGTAGTTGTAAAGCTTGGGGGTAGTTCTCTGACAGATAAGGAAGAGGCATCACTC"
            "AGGCGTTTAGCTGAGCAGATTGCAGCATTAAAAGAGAGTGGCAATAAACTAGTGGTCGTG"
            "CATGGAGGCGGCAGCTTCACTGATGGTCTGCTGGCATTGAAAAGTGGCCTGAGCTCGGGC"
            "GAATTAGCTGCGGGGTTGAGGAGCACGTTAGAAGAGGCCGGAGAAGTAGCGACGAGGGAC"
            "GCCCTAGCTAGCTTAGGGGAACGGCTTGTTGCAGCGCTGCTGGCGGCGGGTCTCCCTGCT"
            "GTAGGACTCAGCGCCGCTGCGTTAGATGCGACGGAGGCGGGCCGGGATGAAGGCAGCGAC"
            "GGGAACGTCGAGTCCGTGGACGCAGAAGCAATTGAGGAGTTGCTTGAGGCCGGGGTGGTC"
            "CCCGTCCTAACAGGATTTATCGGCTTAGACGAAGAAGGGGAACTGGGAAGGGGATCTTCT"
            "GACACCATCGCTGCGTTACTCGCTGAAGCTTTAGGCGCGGACAAACTCATAATACTGACC"
            "GACGTAGACGGCGTTTACGATGCCGACCCTAAAAAGGTCCCAGACGCGAGGCTCTTGCCA"
            "GAGATAAGTGTGGACGAGGCCGAGGAAAGCGCCTCCGAATTAGCGACCGGTGGGATGAAG"
            "GTCAAACATCCAGCGGCTCTTGCTGCAGCTAGACGGGGGGGTATTCCGGTCGTGATAACG"
            "AAT",
        ),
        SeqIn(
            name="23ISL-consensus",
            data="CAGGGTCTGGATAACGCTAATCGTTCGCTAGTTCGCGCTACAAAAGCAGAAAGTTCAGAT"
            "ATACGGAAAGAGGTGACTAACGGCATCGCTAAAGGGCTGAAGCTAGACAGTCTGGAAACA"
            "GCTGCAGAGTCGAAGAACTGCTCAAGCGCACAGAAAGGCGGATCGCTAGCTTGGGCAACC"
            "AACTCCCAACCACAGCCTCTCCGTGAAAGTAAGCTTGAGCCATTGGAAGACTCCCCACGT"
            "AAGGCTTTAAAAACACCTGTGTTGCAAAAGACATCCAGTACCATAACTTTACAAGCAGTC"
            "AAGGTTCAACCTGAACCCCGCGCTCCCGTCTCCGGGGCGCTGTCCCCGAGCGGGGAGGAA"
            "CGCAAGCGCCCAGCTGCGTCTGCTCCCGCTACCTTACCGACACGACAGAGTGGTCTAGGT"
            "TCTCAGGAAGTCGTTTCGAAGGTGGCGACTCGCAAAATTCCAATGGAGTCACAACGCGAG"
            "TCGACT",
        ),
    ],
)


@app.get(
    "/jobs/next_pend",
    summary="get next pending job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_next_pend_job():
    cjob = ffi.new("struct sched_job *")
    rc = RC(lib.sched_job_next_pend(cjob))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "pending job not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return Job.from_cdata(cjob)


@app.get(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_job(job_id: int):
    cjob = ffi.new("struct sched_job *")
    cjob[0].id = job_id

    rc = RC(lib.sched_job_get(cjob))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "job not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return Job.from_cdata(cjob)


@app.patch(
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
        HTTP_403_FORBIDDEN: {"model": ReturnData},
    },
)
def update_job(job_id: int, state: JobState, error: str):
    job = get_job(job_id)

    if job.state == state:
        raise DCPException(
            HTTP_403_FORBIDDEN, Code.EINVAL, "redundant job state update"
        )

    if job.state == JobState.pend and state == JobState.run:

        rc = RC(lib.sched_job_set_run(job_id))
        if rc != RC.DONE:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])
        return get_job(job_id)

    elif job.state == JobState.run and state == JobState.done:

        rc = RC(lib.sched_job_set_done(job_id))
        if rc != RC.DONE:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])
        return get_job(job_id)

    elif job.state == JobState.run and state == JobState.fail:

        rc = RC(lib.sched_job_set_fail(job_id, error.encode()))
        if rc != RC.DONE:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])
        return get_job(job_id)

    raise DCPException(HTTP_403_FORBIDDEN, Code.EINVAL, "invalid job state update")


@app.post(
    "/jobs",
    summary="add job",
    response_model=Job,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def post_job(job: JobIn = Body(..., example=job_in_example)):
    cjob = ffi.new("struct sched_job *")

    cjob[0].id = 0
    cjob[0].db_id = job.db_id
    cjob[0].multi_hits = job.multi_hits
    cjob[0].hmmer3_compat = job.hmmer3_compat

    rc = RC(lib.sched_job_begin_submission(cjob))
    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    for seq in job.seqs:
        lib.sched_job_add_seq(cjob, seq.name.encode(), seq.data.encode())

    rc = RC(lib.sched_job_end_submission(cjob))
    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return Job.from_cdata(cjob)


@ffi.def_extern()
def prod_set_cb(cprod, arg):
    prods = ffi.from_handle(arg)
    prods.append(create_prod(cprod))


@app.get(
    "/jobs/{job_id}/prods",
    summary="get products",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_job_prods(job_id: int):
    cprod = ffi.new("struct sched_prod *")
    prods: List[Prod] = []
    rc = RC(
        lib.sched_job_get_prods(job_id, lib.prod_set_cb, cprod, ffi.new_handle(prods))
    )

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "job not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return prods


@ffi.def_extern()
def seq_set_cb(cseq, arg):
    seqs = ffi.from_handle(arg)
    seqs.append(Seq.from_cdata(cseq))


@app.get(
    "/jobs/{job_id}/seqs/next/{seq_id}",
    summary="get next sequence",
    response_model=Seq,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_next_job_seq(job_id: int, seq_id: int):
    cseq = ffi.new("struct sched_seq *")
    cseq[0].id = seq_id
    cseq[0].job_id = job_id
    rc = RC(lib.sched_seq_next(cseq))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "next sequence not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return Seq.from_cdata(cseq)


@app.get(
    "/jobs/{job_id}/seqs",
    summary="get all sequences of a job",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ReturnData},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
    },
)
def get_job_seqs(job_id: int):
    cseq = ffi.new("struct sched_seq *")
    seqs: List[Seq] = []
    rc = RC(lib.sched_job_get_seqs(job_id, lib.seq_set_cb, cseq, ffi.new_handle(seqs)))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, Code[rc.name], "job not found")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return seqs


@app.get("/prods/upload/example", response_class=PlainTextResponse)
def upload_prods_file_example():
    return examples.prods_file


@app.post(
    "/prods/upload",
    summary="upload a text/tab-separated-values file of products",
    response_model=ReturnData,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReturnData},
        HTTP_409_CONFLICT: {"model": ReturnData},
        HTTP_400_BAD_REQUEST: {"model": ReturnData},
    },
)
def upload_prods_file(prods_file: UploadFile = File(...)):
    prods_file.file.flush()
    fd = os.dup(prods_file.file.fileno())
    fp = lib.fdopen(fd, b"rb")
    rc = RC(lib.sched_prod_add_file(fp))

    if rc == RC.EINVAL:
        raise DCPException(HTTP_409_CONFLICT, Code[rc.name], "constraint violation")

    if rc == RC.EPARSE:
        raise DCPException(HTTP_400_BAD_REQUEST, Code[rc.name], "parse error")

    if rc != RC.DONE:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])

    return ReturnData(rc=Code[rc.name], msg="")


# @app.post("/jobs/{job_id}/prods")
# def post_prod(job_id: int, prod_in: ProdIn = Body(None, example=prod_in_example)):
#     cprod = prod_in._create_cdata()
#     cprod[0].job_id = job_id
#     rc = RC(lib.sched_prod_add(cprod))
#
#     if rc != RC.DONE:
#         raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])
#
#     return get_prod(int(cprod[0].id))
