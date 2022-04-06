from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from deciphon_api.api.api import router as api_router
from deciphon_api.core.config import Settings
from deciphon_api.core.events import create_start_handler, create_stop_handler
from deciphon_api.errors import (
    DeciphonError,
    deciphon_error_handler,
    http422_error_handler,
)

__all__ = ["app", "get_app"]


def get_app() -> FastAPI:
    settings = Settings()

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

    app.add_exception_handler(DeciphonError, deciphon_error_handler)
    app.add_exception_handler(RequestValidationError, http422_error_handler)

    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = get_app()
