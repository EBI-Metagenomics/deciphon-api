from __future__ import annotations

from pathlib import Path
from typing import Any, List, Tuple

from pydantic import BaseModel, Field

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import InternalError, NotFoundError
from deciphon_api.rc import RC

__all__ = ["DB"]


class DB(BaseModel):
    id: int = Field(..., gt=0)
    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = ""
    hmm_id: int = Field(..., gt=0)

    @classmethod
    def from_cdata(cls, cdb):
        return cls(
            id=int(cdb.id),
            xxh3=int(cdb.xxh3),
            filename=ffi.string(cdb.filename).decode(),
            hmm_id=int(cdb.hmm_id),
        )

    @staticmethod
    def add(filename: str):
        if not Path(filename).exists():
            raise NotFoundError("file")

        p_db = ffi.new("struct sched_db *")
        lib.sched_db_init(p_db)

        rc = RC(lib.sched_db_add(p_db, filename.encode()))

        if rc != RC.OK:
            raise InternalError(rc)

        return DB.from_cdata(p_db[0])

    @staticmethod
    def get_by_id(db_id: int) -> DB:
        return resolve_get_db(*get_by_id(db_id))

    @staticmethod
    def get_by_filename(filename: str) -> DB:
        return resolve_get_db(*get_by_filename(filename))

    @staticmethod
    def exists_by_id(db_id: int) -> bool:
        try:
            DB.get_by_id(db_id)
        except NotFoundError:
            return False
        return True

    @staticmethod
    def exists_by_filename(filename: str) -> bool:
        try:
            DB.get_by_filename(filename)
        except NotFoundError:
            return False
        return True

    @staticmethod
    def get_list() -> List[DB]:
        ptr = ffi.new("struct sched_db *")

        dbs: List[DB] = []
        rc = RC(lib.sched_db_get_all(lib.append_db, ptr, ffi.new_handle(dbs)))
        assert rc != RC.END

        if rc != RC.OK:
            raise InternalError(rc)

        return dbs

    @staticmethod
    def remove(db_id: int):
        rc = RC(lib.sched_db_remove(db_id))

        if rc == RC.NOTFOUND:
            raise NotFoundError("db")

        if rc != RC.OK:
            raise InternalError(rc)


def get_by_id(db_id: int) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_db *")

    rc = RC(lib.sched_db_get_by_id(ptr, db_id))
    assert rc != RC.END

    return (ptr, rc)


def get_by_filename(filename: str) -> Tuple[Any, RC]:
    ptr = ffi.new("struct sched_db *")

    rc = RC(lib.sched_db_get_by_filename(ptr, filename.encode()))
    assert rc != RC.END

    return (ptr, rc)


def resolve_get_db(ptr: Any, rc: RC) -> DB:
    if rc == RC.OK:
        return DB.from_cdata(ptr[0])

    if rc == RC.NOTFOUND:
        raise NotFoundError("database")

    raise InternalError(rc)


@ffi.def_extern()
def append_db(ptr, arg):
    dbs = ffi.from_handle(arg)
    dbs.append(DB.from_cdata(ptr[0]))
