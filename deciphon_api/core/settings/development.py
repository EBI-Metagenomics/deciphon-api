import logging

from deciphon_api.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True
    title: str = "Dev Deciphon API"
    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env"
