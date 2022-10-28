from __future__ import annotations

from typing import List

from deciphon_sched.prod import (
    sched_prod,
    sched_prod_add_file,
    sched_prod_get_all,
    sched_prod_get_by_id,
)
from pydantic import BaseModel, Field

__all__ = ["Prod", "Prods"]


class Prod(BaseModel):
    id: int = Field(..., gt=0)

    scan_id: int = Field(..., gt=0)
    seq_id: int = Field(..., gt=0)

    profile_name: str = ""
    abc_name: str = ""

    alt_loglik: float = 0.0
    null_loglik: float = 0.0

    profile_typeid: str = ""
    version: str = ""

    match: str = ""

    @classmethod
    def from_sched_prod(cls, prod: sched_prod):
        return cls(
            id=prod.id,
            scan_id=prod.scan_id,
            seq_id=prod.seq_id,
            profile_name=prod.profile_name,
            abc_name=prod.abc_name,
            alt_loglik=prod.alt_loglik,
            null_loglik=prod.null_loglik,
            profile_typeid=prod.profile_typeid,
            version=prod.version,
            match=prod.match,
        )

    @classmethod
    def get(cls, prod_id: int) -> Prod:
        return Prod.from_sched_prod(sched_prod_get_by_id(prod_id))

    @staticmethod
    def get_list() -> List[Prod]:
        return [Prod.from_sched_prod(prod) for prod in sched_prod_get_all()]

    @staticmethod
    def add_file(file):
        sched_prod_add_file(file)


class Prods(BaseModel):
    __root__: List[Prod]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self) -> int:
        return len(list(self.__root__))
