from __future__ import annotations

from sqlmodel import Field, SQLModel


class ScanBase(SQLModel):
    multi_hits: bool = Field(nullable=False)
    hmmer3_compat: bool = Field(nullable=False)
    db_id: int = Field(foreign_key="db.id")


class ScanCreate(ScanBase):
    ...


class ScanRead(ScanBase):
    ...


class ScanUpdate(SQLModel):
    ...
