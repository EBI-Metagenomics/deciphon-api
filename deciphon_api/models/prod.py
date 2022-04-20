from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from deciphon_api.core.errors import InternalError
from deciphon_api.sched.cffi import ffi, lib
from deciphon_api.sched.prod import sched_prod

__all__ = ["Prod"]


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
    def from_id(cls, prod_id: int):
        ptr = ffi.new("struct sched_prod *")

        rc = RC(lib.sched_prod_get_by_id(ptr, prod_id))
        assert rc != RC.END

        if rc == RC.NOTFOUND:
            raise NotFoundError("prod")

        if rc != RC.OK:
            raise InternalError(rc)

        return Prod.from_cdata(ptr[0])

    @staticmethod
    def get_list() -> List[Prod]:
        ptr = ffi.new("struct sched_prod *")

        prods: List[Prod] = []
        rc = RC(lib.sched_prod_get_all(lib.append_prod, ptr, ffi.new_handle(prods)))
        assert rc != RC.END

        if rc != RC.OK:
            raise InternalError(rc)

        return prods


@ffi.def_extern()
def append_prod(ptr, arg):
    prods = ffi.from_handle(arg)
    prods.append(Prod.from_cdata(ptr[0]))
