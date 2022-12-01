from functools import lru_cache

from sqlalchemy.future import Engine
from sqlmodel import create_engine

from deciphon_api.core.settings import settings

__all__ = ["scheduler"]


@lru_cache
def get_scheduler() -> Engine:
    uri = f"sqlite:///{settings.sched_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(uri, echo=True, connect_args=connect_args)


scheduler = get_scheduler()
