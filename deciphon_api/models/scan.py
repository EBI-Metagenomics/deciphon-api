from typing import List

from pydantic import BaseModel, Field
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import EINVALException, create_exception
from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan_result import ScanResult
from deciphon_api.models.seq import Seq
from deciphon_api.rc import RC

__all__ = ["Scan", "ScanPost"]


class Scan(BaseModel):
    id: int = Field(..., gt=0)
    db_id: int = Field(..., gt=0)

    multi_hits: bool = Field(False)
    hmmer3_compat: bool = Field(False)

    job_id: int = Field(..., gt=0)

    @classmethod
    def from_cdata(cls, cjob):
        return cls(
            id=int(cjob.id),
            db_id=int(cjob.db_id),
            multi_hits=bool(cjob.multi_hits),
            hmmer3_compat=bool(cjob.hmmer3_compat),
            job_id=int(cjob.job_id),
        )

    @classmethod
    def from_id(cls, scan_id: int):
        ptr = ffi.new("struct sched_scan *")

        rc = RC(lib.sched_scan_get_by_id(ptr, scan_id))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "scan not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return Scan.from_cdata(ptr[0])

    def prods(self) -> List[Prod]:
        ptr = ffi.new("struct sched_prod *")
        prods: List[Prod] = []

        prods_hdl = ffi.new_handle(prods)
        rc = RC(lib.sched_scan_get_prods(self.id, lib.append_prod, ptr, prods_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "scan not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return prods

    def seqs(self) -> List[Seq]:
        ptr = ffi.new("struct sched_seq *")
        seqs: List[Seq] = []

        seqs_hdl = ffi.new_handle(seqs)
        rc = RC(lib.sched_scan_get_seqs(self.id, lib.append_seq, ptr, seqs_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise EINVALException(HTTP_404_NOT_FOUND, "scan not found")

        if rc != RC.OK:
            raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return seqs

    def result(self) -> ScanResult:

        job = self.job()

        if job.state != JobState.done:
            raise EINVALException(
                HTTP_412_PRECONDITION_FAILED, "job is not in done state"
            )

        prods: List[Prod] = self.prods()
        seqs: List[Seq] = self.seqs()
        return ScanResult(self, prods, seqs)

    def job(self) -> Job:
        return Job.from_id(self.job_id)


class SeqPost(BaseModel):
    name: str = ""
    data: str = ""


class ScanPost(BaseModel):
    db_id: int = 0

    multi_hits: bool = False
    hmmer3_compat: bool = False

    seqs: List[SeqPost] = []

    @classmethod
    def example(cls):
        return cls(
            db_id=1,
            multi_hits=True,
            hmmer3_compat=False,
            seqs=[
                SeqPost(
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
                SeqPost(
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
                SeqPost(
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
