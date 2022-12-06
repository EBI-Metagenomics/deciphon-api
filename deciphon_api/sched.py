from functools import lru_cache
from typing import TypeAlias

from sqlalchemy.future import Engine
from sqlmodel import create_engine

from deciphon_api.config import get_config

__all__ = ["get_sched", "Sched"]

Sched: TypeAlias = Engine


@lru_cache
def get_sched() -> Sched:
    config = get_config()
    uri = f"sqlite:///{config.sched_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(uri, echo=config.sql_echo, connect_args=connect_args)
