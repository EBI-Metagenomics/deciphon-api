from enum import Enum
from typing import List

from fastapi import Body
from pydantic import BaseModel
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ._app import app
from .csched import ffi, lib
from .exception import DCPException
from .job_result import JobResult
from .prod import Prod
from .rc import RC, StrRC
from ._types import ErrorResponse
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

    @classmethod
    def from_id(cls, job_id: int):
        cjob = ffi.new("struct sched_job *")
        cjob[0].id = job_id

        rc = RC(lib.sched_job_get(cjob))

        if rc == RC.NOTFOUND:
            raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "job not found")

        if rc != RC.OK:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

        return Job.from_cdata(cjob)

    def prods(self) -> List[Prod]:
        cprod = ffi.new("struct sched_prod *")
        prods: List[Prod] = []
        rc = RC(
            lib.sched_job_get_prods(
                self.id, lib.append_prod_callback, cprod, ffi.new_handle(prods)
            )
        )

        if rc == RC.NOTFOUND:
            raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "job not found")

        if rc != RC.OK:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

        return prods

    def seqs(self) -> List[Seq]:
        cseq = ffi.new("struct sched_seq *")
        seqs: List[Seq] = []

        rc = RC(
            lib.sched_job_get_seqs(
                self.id, lib.append_seq_callback, cseq, ffi.new_handle(seqs)
            )
        )
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "job not found")

        if rc != RC.OK:
            raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

        return seqs

    def result(self) -> JobResult:
        prods: List[Prod] = self.prods()
        seqs: List[Seq] = self.seqs()
        return JobResult(self, prods, seqs)


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
    "/jobs/{job_id}",
    summary="get job",
    response_model=Job,
    status_code=HTTP_200_OK,
    responses={
        HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def get_jobs(job_id: int):
    cjob = ffi.new("struct sched_job *")
    cjob[0].id = job_id

    rc = RC(lib.sched_job_get(cjob))

    if rc == RC.NOTFOUND:
        raise DCPException(HTTP_404_NOT_FOUND, StrRC[rc.name], "job not found")

    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return Job.from_cdata(cjob)


@app.post(
    "/jobs",
    summary="add job",
    response_model=Job,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
def post_job(job: JobIn = Body(..., example=job_in_example)):
    cjob = ffi.new("struct sched_job *")

    cjob[0].id = 0
    cjob[0].db_id = job.db_id
    cjob[0].multi_hits = job.multi_hits
    cjob[0].hmmer3_compat = job.hmmer3_compat

    # TODO: implement try-catch all to call sched_job_rollback_submission
    # in case of cancel/failure.
    rc = RC(lib.sched_job_begin_submission(cjob))
    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    for seq in job.seqs:
        lib.sched_job_add_seq(cjob, seq.name.encode(), seq.data.encode())

    rc = RC(lib.sched_job_end_submission(cjob))
    if rc != RC.OK:
        raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, StrRC[rc.name])

    return Job.from_cdata(cjob)


@ffi.def_extern()
def append_prod_callback(cprod, arg):
    prods = ffi.from_handle(arg)
    prods.append(Prod.from_cdata(cprod))


@ffi.def_extern()
def append_seq_callback(cseq, arg):
    seqs = ffi.from_handle(arg)
    seqs.append(Seq.from_cdata(cseq))


# @app.post("/jobs/{job_id}/prods")
# def post_prod(job_id: int, prod_in: ProdIn = Body(None, example=prod_in_example)):
#     cprod = prod_in._create_cdata()
#     cprod[0].job_id = job_id
#     rc = RC(lib.sched_prod_add(cprod))
#
#     if rc != RC.OK:
#         raise DCPException(HTTP_500_INTERNAL_SERVER_ERROR, Code[rc.name])
#
#     return get_prod(int(cprod[0].id))
