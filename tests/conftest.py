import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deciphon_api.main import get_app


@pytest.fixture
def app(tmp_path: Path) -> FastAPI:
    os.chdir(tmp_path)
    return get_app()


@pytest.fixture
def upload_database():
    def upload(client: TestClient, path: Path):
        return client.post(
            "/api/dbs/",
            files={
                "database": (
                    path.name,
                    open(path, "rb"),
                    "application/octet-stream",
                )
            },
        )

    return upload
