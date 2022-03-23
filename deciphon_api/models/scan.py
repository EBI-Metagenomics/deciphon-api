from typing import List

from pydantic import BaseModel, Field

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import InternalError, JobNotDone, ScanNotFound
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
    def from_cdata(cls, cscan):
        return cls(
            id=int(cscan.id),
            db_id=int(cscan.db_id),
            multi_hits=bool(cscan.multi_hits),
            hmmer3_compat=bool(cscan.hmmer3_compat),
            job_id=int(cscan.job_id),
        )

    @classmethod
    def from_id(cls, scan_id: int):
        ptr = ffi.new("struct sched_scan *")

        rc = RC(lib.sched_scan_get_by_id(ptr, scan_id))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise ScanNotFound()

        if rc != RC.OK:
            raise InternalError(rc)

        return Scan.from_cdata(ptr[0])

    def prods(self) -> List[Prod]:
        ptr = ffi.new("struct sched_prod *")
        prods: List[Prod] = []

        prods_hdl = ffi.new_handle(prods)
        rc = RC(lib.sched_scan_get_prods(self.id, lib.append_prod, ptr, prods_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise ScanNotFound()

        if rc != RC.OK:
            raise InternalError(rc)

        return prods

    def seqs(self) -> List[Seq]:
        ptr = ffi.new("struct sched_seq *")
        seqs: List[Seq] = []

        seqs_hdl = ffi.new_handle(seqs)
        rc = RC(lib.sched_scan_get_seqs(self.id, lib.append_seq, ptr, seqs_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise ScanNotFound()

        if rc != RC.OK:
            raise InternalError(rc)

        return seqs

    def result(self) -> ScanResult:

        job = self.job()

        if job.state != JobState.done:
            raise JobNotDone()

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
