from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from deciphon_sched.db import (
    sched_db,
    sched_db_add,
    sched_db_get_all,
    sched_db_get_by_filename,
    sched_db_get_by_hmm_id,
    sched_db_get_by_id,
    sched_db_get_by_xxh3,
    sched_db_remove,
)
from sqlmodel import Field, SQLModel

__all__ = ["DB", "DBIDType", "DBCreate", "DBRead"]


class DBIDType(str, Enum):
    DB_ID = "db_id"
    XXH3 = "xxh3"
    FILENAME = "filename"
    HMM_ID = "hmm_id"


class DBBase(SQLModel):
    xxh3: int = Field(..., title="XXH3 file hash")
    filename: str = Field(..., unique=True, title="File name")
    hmm_id: int = Field(..., gt=0, foreign_key="hmm.id")


class DB(DBBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True, gt=0)

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


class DBCreate(DBBase):
    pass


class DBRead(DBBase):
    id: int
