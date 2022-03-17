from typing import Callable

from loguru import logger

from deciphon_api.core.settings.app import AppSettings

from ..sched import sched_close, sched_open, sched_setup


def create_start_app_handler(
    settings: AppSettings,
) -> Callable:
    async def start_app() -> None:
        logger.info("Starting scheduler")
        sched_setup(str(settings.sched_filename))
        sched_open()

    return start_app


def create_stop_app_handler() -> Callable:
    @logger.catch
    async def stop_app() -> None:
        sched_close()

    return stop_app
