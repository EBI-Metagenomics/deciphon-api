from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ._types import ErrorResponse
from .csched import lib
from .exception import DCPException, create_exception
from .rc import RC

__all__ = ["app"]

app = FastAPI()

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


def sched_setup(file_name: str):
    rc = RC(lib.sched_setup(file_name.encode()))

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)


def sched_open():
    rc = RC(lib.sched_open())

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)


def sched_close():
    rc = RC(lib.sched_close())

    if rc != RC.OK:
        raise create_exception(HTTP_500_INTERNAL_SERVER_ERROR, rc)


@app.on_event("startup")
def startup_event():
    sched_setup("deciphon.sched")
    sched_open()


@app.on_event("shutdown")
def shutdown_event():
    sched_close()


@app.exception_handler(DCPException)
def deciphon_exception_handler(_: Request, exc: DCPException):
    content = ErrorResponse.create(exc.rc, exc.msg)
    return JSONResponse(
        status_code=exc.http_code,
        content=content.dict(),
    )
