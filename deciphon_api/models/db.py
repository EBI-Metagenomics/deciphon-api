from __future__ import annotations

from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field

from deciphon_api.sched.db import (
    sched_db,
    sched_db_add,
    sched_db_get_all,
    sched_db_get_by_filename,
    sched_db_get_by_hmm_id,
    sched_db_get_by_id,
    sched_db_get_by_xxh3,
    sched_db_remove,
)

__all__ = ["DB", "DBIDType"]


class DBIDType(str, Enum):
    DB_ID = "db_id"
    XXH3 = "xxh3"
    FILENAME = "filename"
    HMM_ID = "hmm_id"


class DB(BaseModel):
    id: int = Field(..., gt=0)
    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = ""
    hmm_id: int = Field(..., gt=0)

    @classmethod
    def from_sched_db(cls, db: sched_db):
        return cls(
            id=db.id,
            xxh3=db.xxh3,
            filename=db.filename,
            hmm_id=db.hmm_id,
        )

    @staticmethod
    def add(filename: str):
        return DB.from_sched_db(sched_db_add(filename))

    @staticmethod
    def get(id: Union[int, str], id_type: DBIDType) -> DB:
        # if id_type == DBIDType.FILENAME and not isinstance(id, str):
        #     raise InvalidTypeError("Expected string")
        # elif id_type != DBIDType.FILENAME and not isinstance(id, int):
        #     raise InvalidTypeError("Expected integer")

        if id_type == DBIDType.DB_ID:
            assert isinstance(id, int)
            return DB.from_sched_db(sched_db_get_by_id(id))

        if id_type == DBIDType.XXH3:
            assert isinstance(id, int)
            return DB.from_sched_db(sched_db_get_by_xxh3(id))

        if id_type == DBIDType.FILENAME:
            assert isinstance(id, str)
            return DB.from_sched_db(sched_db_get_by_filename(id))

        if id_type == DBIDType.HMM_ID:
            assert isinstance(id, int)
            return DB.from_sched_db(sched_db_get_by_hmm_id(id))

    @staticmethod
    def get_list() -> List[DB]:
        return [DB.from_sched_db(db) for db in sched_db_get_all()]

    @staticmethod
    def remove(db_id: int):
        sched_db_remove(db_id)
