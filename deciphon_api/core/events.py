from typing import Callable

from loguru import logger

from deciphon_api.core.settings.app import AppSettings
from deciphon_api.sched import sched_cleanup, sched_init


def create_start_app_handler(
    settings: AppSettings,
) -> Callable:
    async def start_app() -> None:
        logger.info("Starting scheduler")
        sched_init(str(settings.sched_filename))

    return start_app


def create_stop_app_handler() -> Callable:
    @logger.catch
    async def stop_app() -> None:
        sched_cleanup()

    return stop_app
