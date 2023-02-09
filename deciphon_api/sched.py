from functools import lru_cache

from sqlalchemy.future import Engine
from sqlmodel import Session, SQLModel, create_engine, select
from typing import Type

from deciphon_api.config import get_config

__all__ = ["Sched", "select"]


@lru_cache
def get_engine() -> Engine:
    config = get_config()
    uri = f"sqlite:///{config.sched_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(uri, echo=config.sql_echo, connect_args=connect_args)


class Sched:
    def __init__(self):
        self._session = Session(get_engine())

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._session.close()

    def add(self, x: SQLModel):
        self._session.add(x)

    def get(self, x: Type[SQLModel], ident):
        return self._session.get(x, ident)

    def exec(self, stmt):
        return self._session.exec(stmt)

    def commit(self):
        self._session.commit()

    def delete(self, x: SQLModel):
        self._session.delete(x)

    def refresh(self, x: SQLModel):
        self._session.refresh(x)

    def close(self):
        self._session.close()
