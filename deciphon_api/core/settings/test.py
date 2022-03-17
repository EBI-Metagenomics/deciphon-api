import logging

from deciphon_api.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True
    title: str = "Test Deciphon API"
    logging_level: int = logging.DEBUG
