from pydantic import BaseModel, Field
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import EINVAL, InternalError
from deciphon_api.rc import RC

__all__ = ["Prod", "ProdID"]


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
            raise EINVAL(HTTP_404_NOT_FOUND, "prod not found")

        if rc != RC.OK:
            raise InternalError(HTTP_500_INTERNAL_SERVER_ERROR, rc)

        return Prod.from_cdata(ptr[0])


class ProdID(BaseModel):
    id: int = Field(..., gt=0)


@ffi.def_extern()
def append_prod(ptr, arg):
    prods = ffi.from_handle(arg)
    prods.append(Prod.from_cdata(ptr[0]))