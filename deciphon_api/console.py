import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
import uvicorn

from deciphon_api.core.settings import settings

__all__ = ["run"]

run = typer.Typer()


@run.command()
def generate_config():
    import deciphon_api.data as data

    typer.echo(data.env_example_content(), nl=False)


@run.command()
def dev():
    host = settings.host
    port = settings.port
    log_level = settings.logging_level
    reload = settings.reload
    uvicorn.run(
        "deciphon_api.main:app",
        host=host,
        port=port,
        log_level=log_level.value,
        reload=reload,
    )


@run.command()
def start(
    daemon: Optional[bool] = typer.Option(False, help="Daemonize it."),
):
    host = settings.host
    port = settings.port
    cmds = [
        str(Path(sys.executable).parent / "gunicorn"),
        "deciphon_api.main:app",
        "--workers",
        "1",
        "--worker-class",
        "uvicorn.workers.UvicornWorker",
        "--bind",
        f"{host}:{port}",
    ]
    if daemon:
        cmds.append("--daemon")
    subprocess.run(cmds)
