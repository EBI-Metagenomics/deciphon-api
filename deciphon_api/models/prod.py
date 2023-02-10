from __future__ import annotations

from sqlmodel import Field, SQLModel, UniqueConstraint
from deciphon_api.filename import filename_regex
from deciphon_api.sha256 import SHA256_REGEX


class ProdBase(SQLModel):
    scan_id: int = Field(foreign_key="scan.id")
    seq_id: int = Field(foreign_key="seq.id")

    profile: str = Field(nullable=False)
    abc: str = Field(nullable=False)

    alt_loglik: float = Field(nullable=False)
    null_loglik: float = Field(nullable=False)
    evalue_log: float = Field(nullable=False)

    match: str = Field(nullable=False)

    sha256: str = Field(index=True, unique=True, regex=SHA256_REGEX)
    filename: str = Field(index=True, unique=True, regex=filename_regex("dcs"))

    __table_args__ = (UniqueConstraint("scan_id", "seq_id", "profile"),)


class ProdCreate(SQLModel):
    sha256: str = Field(regex=SHA256_REGEX)
    filename: str = Field(regex=filename_regex("dcs"))


class ProdRead(ProdBase):
    ...


class ProdUpdate(SQLModel):
    ...
