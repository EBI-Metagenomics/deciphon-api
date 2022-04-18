import typer
import uvicorn

import deciphon_api.data as data
from deciphon_api.core.settings import settings

__all__ = ["run"]

run = typer.Typer()


@run.command()
def generate_config():
    typer.echo(data.env_example_content(), nl=False)


@run.command()
def start():
    host = settings.host
    port = settings.port
    log_level = settings.logging_level
    reload = settings.reload
    uvicorn.run(
        "deciphon_api.main:app.api",
        host=host,
        port=port,
        log_level=log_level.value,
        reload=reload,
    )
