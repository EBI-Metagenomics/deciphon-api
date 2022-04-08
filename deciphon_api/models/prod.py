from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from deciphon_api.core.errors import InternalError, NotFoundError
from deciphon_api.rc import RC
from deciphon_api.sched.cffi import ffi, lib

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
    def from_cdata(cls, cprod):
        return cls(
            id=int(cprod.id),
            scan_id=int(cprod.scan_id),
            seq_id=int(cprod.seq_id),
            profile_name=ffi.string(cprod.profile_name).decode(),
            abc_name=ffi.string(cprod.abc_name).decode(),
            alt_loglik=float(cprod.alt_loglik),
            null_loglik=float(cprod.null_loglik),
            profile_typeid=ffi.string(cprod.profile_typeid).decode(),
            version=ffi.string(cprod.version).decode(),
            match=ffi.string(cprod.match).decode(),
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
