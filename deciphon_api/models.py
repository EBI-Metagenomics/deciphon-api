from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

__all__ = [
    "HMMIn",
    "HMM",
    "DBIn",
    "DB",
    "JobType",
    "JobState",
    "Job",
    "SeqIn",
    "Seq",
    "ScanIn",
    "Scan",
    "ProdIn",
    "Prod",
]

PrimaryKeyType = Optional[int]
ForeignKeyType = int


def PrimaryKeyField():
    return Field(default=None, primary_key=True, nullable=False)


def ForeignKeyField(name: str):
    return Field(foreign_key=name, nullable=False)


def StringIndexField():
    return Field(index=True, unique=True, nullable=False)


def FilenameIndexField(ext: str):
    return Field(
        index=True,
        unique=True,
        nullable=False,
        regex=r"^[0-9a-zA-Z_\-.][0-9a-zA-Z_\-. ]+\." + ext,
    )


def SHA256Field():
    return Field(
        index=True,
        unique=True,
        nullable=False,
        regex=r"^[0123456789abcdef]{64}$",
    )


def SingleRelationship(name: str):
    return Relationship(back_populates=name, sa_relationship_kwargs={"uselist": False})


def ManyRelationship(name: str):
    return Relationship(back_populates=name)


class ProdIn(SQLModel):
    scan_id: ForeignKeyType = ForeignKeyField("scan.id")
    seq_id: ForeignKeyType = ForeignKeyField("seq.id")

    profile: str = Field(nullable=False)
    abc: str = Field(nullable=False)

    alt_loglik: float = Field(nullable=False)
    null_loglik: float = Field(nullable=False)
    evalue_log: float = Field(nullable=False)

    match: str = Field(nullable=False)

    __table_args__ = (UniqueConstraint("scan_id", "seq_id", "profile"),)


class Prod(ProdIn, table=True):
    id: PrimaryKeyType = PrimaryKeyField()
    seq: Seq = SingleRelationship("prod")
    scan: Scan = SingleRelationship("prods")


class SeqIn(SQLModel):
    name: str = Field(nullable=False)
    data: str = Field(nullable=False)


class Seq(SeqIn, table=True):
    id: PrimaryKeyType = PrimaryKeyField()
    scan_id: ForeignKeyType = ForeignKeyField("scan.id")
    scan: Scan = SingleRelationship("seqs")
    prod: Optional[Prod] = SingleRelationship("seq")


class ScanIn(SQLModel):
    multi_hits: bool = Field(True, nullable=False)
    hmmer3_compat: bool = Field(False, nullable=False)
    db_id: ForeignKeyType = ForeignKeyField("db.id")


class Scan(ScanIn, table=True):
    id: PrimaryKeyType = PrimaryKeyField()
    db: DB = SingleRelationship("scans")
    job_id: ForeignKeyType = ForeignKeyField("job.id")
    job: Job = SingleRelationship("scan")
    seqs: List[Seq] = ManyRelationship("scan")
    prods: List[Prod] = ManyRelationship("scan")


class DBIn(SQLModel):
    sha256: str = SHA256Field()
    filename: str = FilenameIndexField("dcp")


class DB(DBIn, table=True):
    id: PrimaryKeyType = PrimaryKeyField()
    hmm_id: ForeignKeyType = ForeignKeyField("hmm.id")
    hmm: HMM = SingleRelationship("db")
    scans: List[Scan] = ManyRelationship("db")


class HMMIn(SQLModel):
    sha256: str = SHA256Field()
    filename: str = FilenameIndexField("hmm")


class HMM(HMMIn, table=True):
    id: PrimaryKeyType = PrimaryKeyField()
    job_id: ForeignKeyType = ForeignKeyField("job.id")
    job: Job = Relationship(back_populates="hmm")
    db: Optional[DB] = SingleRelationship("hmm")


class JobType(Enum):
    hmm = "hmm"
    scan = "scan"


class JobState(Enum):
    pend = "pend"
    run = "run"
    done = "done"
    fail = "fail"


class Job(SQLModel, table=True):
    id: PrimaryKeyType = PrimaryKeyField()

    type: JobType = Field(nullable=False)

    state: JobState = Field(default=JobState.pend, nullable=False)
    progress: int = Field(default=0, ge=0, le=100, nullable=False)

    error: str = Field(default="", nullable=False)

    submission: datetime = Field(default_factory=datetime.now, nullable=False)
    exec_started: Optional[datetime] = Field(default=None, nullable=True)
    exec_ended: Optional[datetime] = Field(default=None, nullable=True)

    hmm: Optional[HMM] = SingleRelationship("job")
    scan: Optional[Scan] = SingleRelationship("job")
