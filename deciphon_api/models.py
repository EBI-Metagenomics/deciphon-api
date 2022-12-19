from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from deciphon_api.exceptions import NotFoundException
from deciphon_api.hmm_path import HMMPath as HMMPath
from deciphon_api.hmmer_path import HMMERPath as HMMERPath
from deciphon_api.hmmer_result import HMMERResult


class JobType(Enum):
    hmm = "hmm"
    scan = "scan"


class JobState(Enum):
    pend = "pend"
    run = "run"
    done = "done"
    fail = "fail"


SINGLE = {"sa_relationship_kwargs": {"uselist": False}}


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: JobType

    state: JobState = JobState.pend
    progress: int = Field(default=0, ge=0, le=100)

    error: Optional[str] = None

    submission: datetime = Field(default_factory=datetime.now)
    exec_started: Optional[datetime] = Field(default=None)
    exec_ended: Optional[datetime] = Field(default=None)

    hmm: HMM = Relationship(back_populates="job", **SINGLE)
    scan: Scan = Relationship(back_populates="job", **SINGLE)


class ProfileType(Enum):
    standard = "stantard"
    protein = "protein"


class HMM(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = Field(..., index=True, unique=True, title="File name")

    job_id: int = Field(default=None, foreign_key="job.id", nullable=False)
    job: Job = Relationship(back_populates="hmm")

    db: DB = Relationship(back_populates="hmm", **SINGLE)


class Match(SQLModel):
    scan_id: int = Field(default=None, foreign_key="scan.id", nullable=False)
    seq_id: int = Field(default=None, foreign_key="seq.id", nullable=False)

    profile: str
    abc: str

    alt_loglik: float
    null_loglik: float
    evalue_log: float

    proftype: ProfileType
    version: str

    match: str

    __table_args__ = (UniqueConstraint("scan_id", "seq_id", "profile"),)


def is_core_state(state: str):
    return state.startswith("M") or state.startswith("I") or state.startswith("D")


class Prod(Match, table=True):
    id: int = Field(default=None, primary_key=True)

    hmmer_sha256: str

    seq: Seq = Relationship(back_populates="prod", **SINGLE)
    scan: Scan = Relationship(back_populates="prods", **SINGLE)

    def _stream(self, name: str, idx: int):
        if name == "frag":
            name_idx = 0
        elif name == "state":
            name_idx = 1
        elif name == "codon":
            name_idx = 2
        elif name == "amino":
            name_idx = 3
        else:
            raise ValueError(f"Invalid stream name: {name}")

        stream = []
        for m in self.match.split(";"):
            value = m.split(",")[name_idx]
            stream.append(value[idx] if len(value) > idx else " ")
        return "".join(stream)

    def hit_bounds(self):
        hit_start = 0
        hit_end = 0
        hit_bounds = []
        offset = 0
        hit_start_found = False
        hit_end_found = False
        for m in self.match.split(";"):
            frag, state = m.split(",")[:2]
            if not hit_start_found and is_core_state(state):
                hit_start = offset
                hit_start_found = True

            if hit_start_found and not is_core_state(state):
                hit_end = offset + len(frag)
                hit_end_found = True

            if hit_end_found:
                hit_bounds.append((hit_start, hit_end))
                hit_start_found = False
                hit_end_found = False

            offset += len(frag)
        return hit_bounds

    def frag_stream(self, idx: int):
        return self._stream("frag", idx)

    def state_stream(self, idx: int):
        return self._stream("state", idx)

    def codon_stream(self, idx: int):
        return self._stream("codon", idx)

    def amino_stream(self, idx: int):
        return self._stream("amino", idx)

    def hmmer(self):
        from deciphon_api.depo import get_depo

        return HMMERResult(get_depo().fetch_blob(self.hmmer_sha256))


class Seq(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    scan_id: int = Field(default=None, foreign_key="scan.id", nullable=False)
    scan: Scan = Relationship(back_populates="seqs", **SINGLE)

    name: str
    data: str

    prod: Optional[Prod] = Relationship(back_populates="seq", **SINGLE)


class Scan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    multi_hits: bool = Field(True)
    hmmer3_compat: bool = Field(False)

    db_id: int = Field(default=None, foreign_key="db.id", nullable=False)
    db: DB = Relationship(back_populates="scans", **SINGLE)

    job_id: int = Field(default=None, foreign_key="job.id", nullable=False)
    job: Job = Relationship(back_populates="scan", **SINGLE)

    seqs: list[Seq] = Relationship(back_populates="scan")
    prods: list[Prod] = Relationship(back_populates="scan")

    def get_prod(self, prod_id: int):
        for prod in self.prods:
            if prod.id == prod_id:
                return prod
        raise NotFoundException(Prod)


class DB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = Field(..., index=True, unique=True, title="File name")

    hmm_id: int = Field(default=None, foreign_key="hmm.id", nullable=False)
    hmm: HMM = Relationship(back_populates="db", **SINGLE)

    scans: list[Scan] = Relationship(back_populates="db")
