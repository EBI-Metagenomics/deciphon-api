from functools import lru_cache

from deciphon_sched.error import SchedError, SchedWrapperError
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from deciphon_api.api.api import router as api_router
from deciphon_api.core.errors import (
    http422_error_handler,
    http_error_handler,
    sched_error_handler,
)
from deciphon_api.core.events import create_start_handler, create_stop_handler
from deciphon_api.core.settings import settings

__all__ = ["app", "settings"]


@lru_cache
def get_app() -> FastAPI:
    settings.configure_logging()

    app = FastAPI(**settings.fastapi_kwargs)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler(
        "startup",
        create_start_handler(settings),
    )
    app.add_event_handler(
        "shutdown",
        create_stop_handler(),
    )

    app.add_exception_handler(SchedError, sched_error_handler)
    app.add_exception_handler(SchedWrapperError, sched_error_handler)

    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, http422_error_handler)

    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = get_app()
