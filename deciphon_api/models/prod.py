from __future__ import annotations

from deciphon_sched.prod import (
    sched_prod,
    sched_prod_add_file,
    sched_prod_get_all,
    sched_prod_get_by_id,
)
from pydantic import BaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

__all__ = ["Prod", "Prods", "ProdRead", "ProdCreate"]


class ProdBase(SQLModel):
    scan_id: int = Field(..., foreign_key="scan.id", gt=0)
    seq_id: int = Field(..., foreign_key="seq.id", gt=0)

    profile: str
    abc: str

    alt_loglik: float
    null_loglik: float
    evalue_log: float

    proftype: ProfileType
    version: str

    match: str

    __table_args__ = (UniqueConstraint("scan_id", "seq_id", "profile"),)


class Prod(ProdBase, table=True):
    id: int = Field(..., gt=0)

    @classmethod
    def from_sched_prod(cls, prod: sched_prod):
        return cls(
            id=prod.id,
            scan_id=prod.scan_id,
            seq_id=prod.seq_id,
            profile=prod.profile_name,
            abc=prod.abc_name,
            alt_loglik=prod.alt_loglik,
            null_loglik=prod.null_loglik,
            evalue_log=0.0,
            proftype=prod.profile_typeid,
            version=prod.version,
            match=prod.match,
        )

    @classmethod
    def get(cls, prod_id: int) -> Prod:
        return Prod.from_sched_prod(sched_prod_get_by_id(prod_id))

    @staticmethod
    def get_list() -> Prods:
        return Prods.create(sched_prod_get_all())

    @staticmethod
    def add_file(file):
        sched_prod_add_file(file)


class Prods(BaseModel):
    __root__: list[Prod]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self) -> int:
        return len(list(self.__root__))

    @classmethod
    def create(cls, prods: list[sched_prod]):
        return Prods(
            __root__=[
                Prod.from_sched_prod(prod)
                for prod in sorted(prods, key=lambda prod: prod.seq_id)
            ]
        )


class ProdCreate(ProdBase):
    pass


class ProdRead(ProdBase):
    id: int
