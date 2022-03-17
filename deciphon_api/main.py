from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ._types import ErrorResponse
from .api.api import router as api_router
from .core.config import get_app_settings
from .core.events import create_start_app_handler, create_stop_app_handler
from .exception import DCPException

__all__ = ["app", "get_app"]


def deciphon_exception_handler(_: Request, exc: DCPException):
    content = ErrorResponse.create(exc.rc, exc.msg)
    return JSONResponse(
        status_code=exc.http_code,
        content=content.dict(),
    )


def get_app() -> FastAPI:
    settings = get_app_settings()

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
        create_start_app_handler(settings),
    )
    app.add_event_handler(
        "shutdown",
        create_stop_app_handler(),
    )

    app.add_exception_handler(DCPException, deciphon_exception_handler)

    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = get_app()
