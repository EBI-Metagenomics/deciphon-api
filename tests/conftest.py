import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import deciphon_api.data as data
import deciphon_api.main as main


@pytest.fixture
def app(tmp_path: Path) -> main.App:
    os.chdir(tmp_path)
    return main.app


def _upload(
    client: TestClient, file_type: str, file_field: str, api_prefix: str, path: Path
):
    return client.post(
        f"{api_prefix}/{file_type}/",
        files={
            file_field: (
                path.name,
                open(path, "rb"),
                "application/octet-stream",
            )
        },
    )


@pytest.fixture
def upload_minifam_hmm():
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)

    def upload(client: TestClient, api_prefix: str):
        return _upload(client, "hmms", "hmm_file", api_prefix, minifam_hmm)

    return upload


@pytest.fixture
def upload_minifam_db():
    minifam_dcp = data.filepath(data.FileName.minifam_db)

    def upload(client: TestClient, api_prefix: str):
        return _upload(client, "dbs", "db_file", api_prefix, minifam_dcp)

    return upload


@pytest.fixture
def upload_minifam(upload_minifam_hmm, upload_minifam_db):
    def upload(client: TestClient, api_prefix: str):
        response = upload_minifam_hmm(client, api_prefix)
        assert response.status_code == 201

        response = upload_minifam_db(client, api_prefix)
        assert response.status_code == 201

    return upload


@pytest.fixture
def upload_pfam1_hmm():
    pfam1_hmm = data.filepath(data.FileName.pfam1_hmm)

    def upload(client: TestClient, api_prefix: str):
        return _upload(client, "hmms", "hmm_file", api_prefix, pfam1_hmm)

    return upload


@pytest.fixture
def upload_pfam1_db():
    pfam1_dcp = data.filepath(data.FileName.pfam1_db)

    def upload(client: TestClient, api_prefix: str):
        return _upload(client, "dbs", "db_file", api_prefix, pfam1_dcp)

    return upload


@pytest.fixture
def upload_pfam1(upload_pfam1_hmm, upload_pfam1_db):
    def upload(client: TestClient, api_prefix: str):
        response = upload_pfam1_hmm(client, api_prefix)
        assert response.status_code == 201

        response = upload_pfam1_db(client, api_prefix)
        assert response.status_code == 201

    return upload
