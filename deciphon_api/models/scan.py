from __future__ import annotations

from enum import Enum
from typing import List

from deciphon_sched.job import sched_job_submit
from deciphon_sched.scan import (
    sched_scan,
    sched_scan_add_seq,
    sched_scan_get_all,
    sched_scan_get_by_id,
    sched_scan_get_by_job_id,
    sched_scan_get_prods,
    sched_scan_get_seqs,
    sched_scan_new,
)
from pydantic import BaseModel, Field

from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod, Prods
from deciphon_api.models.scan_result import ScanResult
from deciphon_api.models.seq import Seq, SeqPost, Seqs

__all__ = ["Scan", "ScanConfig", "ScanPost"]


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

    def prods(self) -> Prods:
        return Prods(
            __root__=[
                Prod.from_sched_prod(prod) for prod in sched_scan_get_prods(self.id)
            ]
        )

    def seqs(self) -> Seqs:
        return Seqs(
            __root__=[Seq.from_sched_seq(seq) for seq in sched_scan_get_seqs(self.id)]
        )

    def result(self) -> ScanResult:
        job = self.job()
        job.assert_state(JobState.SCHED_DONE)

        prods: List[Prod] = self.prods()
        seqs: Seqs = self.seqs()
        return ScanResult(self, prods, seqs)

    def job(self) -> Job:
        return Job.get(self.job_id)

    @staticmethod
    def get_list() -> List[Scan]:
        return [Scan.from_sched_scan(scan) for scan in sched_scan_get_all()]


class ScanConfig(BaseModel):
    db_id: int = Field(..., gt=0)
    multi_hits: bool = False
    hmmer3_compat: bool = False


class ScanPost(BaseModel):
    config: ScanConfig

    seqs: List[SeqPost] = []

    def submit(self) -> Job:
        cfg = self.config
        scan = sched_scan_new(cfg.db_id, cfg.multi_hits, cfg.hmmer3_compat)
        for seq in self.seqs:
            sched_scan_add_seq(seq.name, seq.data)
        return Job.from_sched_job(sched_job_submit(scan))
