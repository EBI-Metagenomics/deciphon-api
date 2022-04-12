import typer
import uvicorn

import deciphon_api.data as data
from deciphon_api.core.settings import get_settings

__all__ = ["run"]

settings = get_settings()
run = typer.Typer()


@run.command()
def generate_config():
    typer.echo(data.env_example_content(), nl=False)


@run.command()
def start():
    host = settings.host
    port = settings.port
    log_level = settings.logging_level
    uvicorn.run("deciphon_api.main:app.api", host=host, port=port, log_level=log_level)
