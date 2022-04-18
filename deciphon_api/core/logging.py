import logging
from enum import Enum
from functools import lru_cache
from types import FrameType
from typing import cast

from loguru import logger

__all__ = ["get_intercept_handler", "LoggingLevel"]


import logging
from enum import Enum


class LoggingLevel(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = "notset"

    @property
    def level(self) -> int:
        return logging.getLevelName(self.name)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


@lru_cache
def get_intercept_handler(logging_level: int) -> InterceptHandler:
    return InterceptHandler(logging_level)
