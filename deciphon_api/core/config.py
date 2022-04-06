import logging
import sys
from typing import Any, Dict, List

from loguru import logger
from pydantic import BaseSettings

from deciphon_api import __version__
from deciphon_api.core.logging import InterceptHandler

__all__ = ["Settings"]


class Settings(BaseSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Deciphon API"
    version: str = __version__

    api_prefix: str = "/api"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    # Refer to loguru format.
    logging_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    sched_filename: str = "deciphon.sched"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler(level=self.logging_level)]

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = []

        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "level": self.logging_level,
                    "format": self.logging_format,
                }
            ]
        )
