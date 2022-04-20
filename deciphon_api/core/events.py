from typing import Callable

from loguru import logger

from deciphon_api.core.settings import Settings
from deciphon_api.sched.sched import sched_cleanup, sched_init

__all__ = ["create_start_handler", "create_stop_handler"]


def create_start_handler(
    settings: Settings,
) -> Callable:
    async def start_app() -> None:
        logger.info("Starting scheduler")
        sched_init(str(settings.sched_filename))

    return start_app


def create_stop_handler() -> Callable:
    @logger.catch
    async def stop_app() -> None:
        sched_cleanup()

    return stop_app
