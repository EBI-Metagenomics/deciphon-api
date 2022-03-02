from . import dbs, endpoint, exception, prods, sched
from ._app import app
from ._version import version as __version__

__name__ = "deciphon_api"

__all__ = [
    "endpoint",
    "sched",
    "dbs",
    "exception",
    "prods",
    "__version__",
    "app",
    "__name__",
]


@app.get("/")
def read_root():
    return {"Hello": "World"}
