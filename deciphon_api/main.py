from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deciphon_api.api.api import router as api_router
from deciphon_api.core.errors import sched_error_handler
from deciphon_api.core.events import create_start_handler, create_stop_handler
from deciphon_api.core.settings import settings
from deciphon_api.sched.error import SchedError, SchedWrapperError

__all__ = ["App", "app"]


class App:
    def __init__(self):

        settings.configure_logging()

        api = FastAPI(**settings.fastapi_kwargs)

        api.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_hosts,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        api.add_event_handler(
            "startup",
            create_start_handler(settings),
        )
        api.add_event_handler(
            "shutdown",
            create_stop_handler(),
        )

        api.add_exception_handler(SchedError, sched_error_handler)
        api.add_exception_handler(SchedWrapperError, sched_error_handler)

        api.include_router(api_router, prefix=settings.api_prefix)

        self._settings = settings
        self._api = api

    @property
    def api(self) -> FastAPI:
        return self._api

    @property
    def api_prefix(self) -> str:
        return self._settings.api_prefix

    @property
    def api_key(self) -> str:
        return self._settings.api_key


@lru_cache
def get_add() -> App:
    return App()


app = get_add()
