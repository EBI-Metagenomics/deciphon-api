from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from deciphon_api.core.errors import NotFoundError
from deciphon_api.sched.db import (
    sched_db,
    sched_db_add,
    sched_db_get_all,
    sched_db_get_by_filename,
    sched_db_get_by_id,
    sched_db_remove,
)

__all__ = ["DB"]


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
        if not Path(filename).exists():
            raise NotFoundError(filename)
        return DB.from_sched_db(sched_db_add(filename))

    @staticmethod
    def get_by_id(db_id: int) -> DB:
        return DB.from_sched_db(sched_db_get_by_id(db_id))

    @staticmethod
    def get_by_filename(filename: str) -> DB:
        return DB.from_sched_db(sched_db_get_by_filename(filename))

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
        return [DB.from_sched_db(db) for db in sched_db_get_all()]

    @staticmethod
    def remove(db_id: int):
        sched_db_remove(db_id)
