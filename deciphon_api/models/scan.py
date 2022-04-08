from __future__ import annotations

from typing import Any, List, Tuple

from pydantic import BaseModel, Field

from deciphon_api.core.errors import ConditionError, InternalError, NotFoundError
from deciphon_api.models.db import DB
from deciphon_api.models.job import Job, JobState
from deciphon_api.models.prod import Prod
from deciphon_api.models.scan_result import ScanResult
from deciphon_api.models.seq import Seq, SeqPost
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

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
    def get_by_id(cls, scan_id: int) -> Scan:
        return resolve_get_scan(*get_by_id(scan_id))

    @staticmethod
    def get_by_job_id(job_id: int) -> Scan:
        return resolve_get_scan(*get_by_job_id(job_id))

    def prods(self) -> List[Prod]:
        ptr = ffi.new("struct sched_prod *")
        prods: List[Prod] = []

        prods_hdl = ffi.new_handle(prods)
        rc = RC(lib.sched_scan_get_prods(self.id, lib.append_prod, ptr, prods_hdl))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise NotFoundError("scan")

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
            raise NotFoundError("scan")

        if rc != RC.OK:
            raise InternalError(rc)

        return seqs

    def result(self) -> ScanResult:
        job = self.job()
        job.assert_state(JobState.done)

        prods: List[Prod] = self.prods()
        seqs: List[Seq] = self.seqs()
        return ScanResult(self, prods, seqs)

    def job(self) -> Job:
        return Job.from_id(self.job_id)

    @staticmethod
    def get_list() -> List[Scan]:
        ptr = ffi.new("struct sched_scan *")

        scans: List[Scan] = []
        rc = RC(lib.sched_scan_get_all(lib.append_scan, ptr, ffi.new_handle(scans)))
        assert rc != RC.END

        if rc != RC.OK:
            raise InternalError(rc)

        return scans


def get_by_id(scan_id: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_scan *")

    rc = RC(lib.sched_scan_get_by_id(ptr, scan_id))
    assert rc != RC.END

    return (ptr, rc)


def get_by_job_id(job_id: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_scan *")

    rc = RC(lib.sched_scan_get_by_job_id(ptr, job_id))
    assert rc != RC.END

    return (ptr, rc)


def resolve_get_scan(ptr: Any, rc: RC) -> Scan:
    if rc == RC.OK:
        return Scan.from_cdata(ptr[0])

    if rc == RC.NOTFOUND:
        raise NotFoundError("scan")

    raise InternalError(rc)


class ScanPost(BaseModel):
    db_id: int = 0

    multi_hits: bool = False
    hmmer3_compat: bool = False

    seqs: List[SeqPost] = []

    def submit(self):
        if not DB.exists_by_id(self.db_id):
            raise NotFoundError("database")

        seqs = self.seqs
        if len(seqs) > lib.NUM_SEQS_PER_JOB:
            raise ConditionError("too many sequences")

        scan_ptr = ffi.new("struct sched_scan *")
        lib.sched_scan_init(scan_ptr, self.db_id, self.multi_hits, self.hmmer3_compat)

        for seq in self.seqs:
            lib.sched_scan_add_seq(scan_ptr, seq.name.encode(), seq.data.encode())

        job_ptr = ffi.new("struct sched_job *")
        lib.sched_job_init(job_ptr, lib.SCHED_SCAN)
        rc = RC(lib.sched_job_submit(job_ptr, scan_ptr))
        assert rc != RC.END
        assert rc != RC.NOTFOUND

        if rc != RC.OK:
            raise InternalError(rc)

        return Job.from_cdata(job_ptr[0])

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


@ffi.def_extern()
def append_scan(ptr, arg):
    scans = ffi.from_handle(arg)
    scans.append(Scan.from_cdata(ptr[0]))
