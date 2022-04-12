import typer
import uvicorn

from deciphon_api.core.settings import get_settings

__all__ = ["run"]

settings = get_settings()
run = typer.Typer()


@run.command()
def start():
    host = settings.host
    port = settings.port
    log_level = settings.logging_level
    uvicorn.run("deciphon_api.main:app.api", host=host, port=port, log_level=log_level)
