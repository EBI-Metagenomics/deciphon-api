from pydantic import BaseModel

from .csched import ffi

__all__ = ["Prod", "ProdID"]


class Prod(BaseModel):
    id: int = 0

    job_id: int = 0
    seq_id: int = 0

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
            id=int(cprod[0].id),
            job_id=int(cprod[0].job_id),
            seq_id=int(cprod[0].seq_id),
            profile_name=ffi.string(cprod[0].profile_name).decode(),
            abc_name=ffi.string(cprod[0].abc_name).decode(),
            alt_loglik=float(cprod[0].alt_loglik),
            null_loglik=float(cprod[0].null_loglik),
            profile_typeid=ffi.string(cprod[0].profile_typeid).decode(),
            version=ffi.string(cprod[0].version).decode(),
            match=ffi.string(cprod[0].match).decode(),
        )


class ProdID(BaseModel):
    id: int = 0
