from __future__ import annotations

from sqlmodel import Field, SQLModel, UniqueConstraint


class ProdBase(SQLModel):
    scan_id: int = Field(foreign_key="scan.id")
    seq_id: int = Field(foreign_key="seq.id")

    profile: str = Field(nullable=False)
    abc: str = Field(nullable=False)

    alt_loglik: float = Field(nullable=False)
    null_loglik: float = Field(nullable=False)
    evalue_log: float = Field(nullable=False)

    match: str = Field(nullable=False)

    __table_args__ = (UniqueConstraint("scan_id", "seq_id", "profile"),)


class ProdCreate(ProdBase):
    ...


class ProdRead(ProdBase):
    ...


class ProdUpdate(SQLModel):
    ...
