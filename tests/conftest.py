import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.main import get_app


@pytest.fixture
def app(tmp_path: Path) -> FastAPI:
    os.chdir(tmp_path)
    return get_app()


@pytest.fixture
def upload_hmm():
    def upload(client: TestClient, path: Path):
        return client.post(
            "/api/hmms/",
            files={
                "hmm_file": (
                    path.name,
                    open(path, "rb"),
                    "application/octet-stream",
                )
            },
        )

    return upload


@pytest.fixture
def upload_database():
    def upload(client: TestClient, path: Path):
        return client.post(
            "/api/dbs/",
            files={
                "database_file": (
                    path.name,
                    open(path, "rb"),
                    "application/octet-stream",
                )
            },
        )

    return upload


@pytest.fixture
def upload_minifam(upload_hmm, upload_database):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)
    minifam_dcp = data.filepath(data.FileName.minifam_dcp)

    def upload(client: TestClient):
        response = upload_hmm(client, minifam_hmm)
        assert response.status_code == 201

        response = upload_database(client, minifam_dcp)
        assert response.status_code == 201

    return upload
