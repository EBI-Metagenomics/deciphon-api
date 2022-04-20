from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan_result import ScanResult
from deciphon_api.models.seq import Seq, SeqPost
from deciphon_api.sched.job import sched_job_submit
from deciphon_api.sched.scan import (
    sched_scan,
    sched_scan_add_seq,
    sched_scan_get_all,
    sched_scan_get_by_id,
    sched_scan_get_by_job_id,
    sched_scan_get_prods,
    sched_scan_get_seqs,
    sched_scan_new,
)

__all__ = ["Scan", "ScanPost"]


class ScanIDType(str, Enum):
    SCAN_ID = "scan_id"
    JOB_ID = "job_id"


class Scan(BaseModel):
    id: int = Field(..., gt=0)
    db_id: int = Field(..., gt=0)

    multi_hits: bool = Field(True)
    hmmer3_compat: bool = Field(False)

    job_id: int = Field(..., gt=0)

    @classmethod
    def from_sched_scan(cls, scan: sched_scan):
        return cls(
            id=scan.id,
            db_id=scan.db_id,
            multi_hits=scan.multi_hits,
            hmmer3_compat=scan.hmmer3_compat,
            job_id=scan.job_id,
        )

    @classmethod
    def get(cls, id: int, id_type: ScanIDType) -> Scan:
        if id_type == ScanIDType.SCAN_ID:
            return Scan.from_sched_scan(sched_scan_get_by_id(id))

        if id_type == ScanIDType.JOB_ID:
            return Scan.from_sched_scan(sched_scan_get_by_job_id(id))

    def prods(self) -> List[Prod]:
        return [Prod.from_sched_prod(prod) for prod in sched_scan_get_prods(self.id)]

    def seqs(self) -> List[Seq]:
        return [Seq.from_sched_seq(seq) for seq in sched_scan_get_seqs(self.id)]

    def result(self) -> ScanResult:
        job = self.job()
        job.assert_state(JobState.SCHED_DONE)

        prods: List[Prod] = self.prods()
        seqs: List[Seq] = self.seqs()
        return ScanResult(self, prods, seqs)

    def job(self) -> Job:
        return Job.get(self.job_id)

    @staticmethod
    def get_list() -> List[Scan]:
        return [Scan.from_sched_scan(scan) for scan in sched_scan_get_all()]


class ScanPost(BaseModel):
    db_id: int = 0

    multi_hits: bool = False
    hmmer3_compat: bool = False

    seqs: List[SeqPost] = []

    def submit(self) -> Job:
        scan = sched_scan_new(self.db_id, self.multi_hits, self.hmmer3_compat)
        for seq in self.seqs:
            sched_scan_add_seq(seq.name, seq.data)
        return Job.from_sched_job(sched_job_submit(scan))

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
