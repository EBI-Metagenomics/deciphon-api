from enum import Enum
from typing import List

from pydantic import BaseModel
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from .csched import ffi, lib
from .exception import EINVALException, create_exception
from .job_result import JobResult
from .prod import Prod
from .rc import RC
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
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return Job.from_cdata(cjob)

    def prods(self) -> List[Prod]:
        cprod = ffi.new("struct sched_prod *")
        prods: List[Prod] = []

        rc = RC(
            lib.sched_job_get_prods(
                self.id, lib.append_prod_callback, cprod, ffi.new_handle(prods)
            )
        )
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

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
            raise EINVALException(HTTP_404_NOT_FOUND, "job not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

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


@ffi.def_extern()
def append_prod_callback(cprod, arg):
    prods = ffi.from_handle(arg)
    prods.append(Prod.from_cdata(cprod))


@ffi.def_extern()
def append_seq_callback(cseq, arg):
    seqs = ffi.from_handle(arg)
    seqs.append(Seq.from_cdata(cseq))
