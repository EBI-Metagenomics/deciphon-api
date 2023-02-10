from typing import Callable, TypeAlias

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlmodel import SQLModel

from deciphon_api.config import get_config
from deciphon_api.depo import get_depo
from deciphon_api.sched import get_engine
from sqlalchemy.exc import IntegrityError
from deciphon_api.errors import integrity_error_handler

__all__ = ["get_app", "App"]

App: TypeAlias = FastAPI


def create_start_handler() -> Callable:
    async def start_app() -> None:
        SQLModel.metadata.create_all(get_engine())

    return start_app


def create_stop_handler() -> Callable:
    @logger.catch
    async def stop_app() -> None:
        get_depo.cache_clear()
        get_engine.cache_clear()
        get_config.cache_clear()

    return stop_app


def get_app() -> App:
    from deciphon_api.api.api import router as api_router

    config = get_config()
    config.configure_logging()

    app = FastAPI(**config.fastapi_kwargs)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler(
        "startup",
        create_start_handler(),
    )
    app.add_event_handler(
        "shutdown",
        create_stop_handler(),
    )

    app.add_exception_handler(IntegrityError, integrity_error_handler)

    app.include_router(api_router, prefix=config.api_prefix)

    return app
