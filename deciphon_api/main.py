from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ._types import ErrorResponse
from .api.api import router as api_router
from .exception import DCPException
from .sched import sched_close, sched_open, sched_setup

__all__ = ["app", "get_app"]


def startup_event():
    sched_setup("deciphon.sched")
    sched_open()


def shutdown_event():
    sched_close()


def deciphon_exception_handler(_: Request, exc: DCPException):
    content = ErrorResponse.create(exc.rc, exc.msg)
    return JSONResponse(
        status_code=exc.http_code,
        content=content.dict(),
    )


def get_app() -> FastAPI:

    app = FastAPI(title="Deciphon API")

    origins = [
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    app.add_event_handler(
        "startup",
        startup_event,
    )
    app.add_event_handler(
        "shutdown",
        shutdown_event,
    )

    app.add_exception_handler(DCPException, deciphon_exception_handler)

    return app


app = get_app()
