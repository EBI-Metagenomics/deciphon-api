from . import sched
from . import job
from . import db
from . import seq
from . import prod
from . import exception
from ._app import app
from ._version import version as __version__

__name__ = "deciphon_api"

__all__ = [
    "sched",
    "db",
    "seq",
    "job",
    "exception",
    "prod",
    "__version__",
    "app",
    "__name__",
]


@app.get("/")
def read_root():
    return {"Hello": "World"}
