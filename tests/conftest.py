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
    client: TestClient,
    file_type: str,
    file_field: str,
    app: main.App,
    path: Path,
):
    return client.post(
        f"{app.api_prefix}/{file_type}/",
        files={
            file_field: (
                path.name,
                open(path, "rb"),
                "application/octet-stream",
            )
        },
        headers={"Authorization": f"Bearer {app.api_key}"},
    )


@pytest.fixture
def upload_minifam_hmm():
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)

    def upload(client: TestClient, app: main.App):
        return _upload(client, "hmms", "hmm_file", app, minifam_hmm)

    return upload


@pytest.fixture
def upload_minifam_db():
    minifam_dcp = data.filepath(data.FileName.minifam_db)

    def upload(client: TestClient, app: main.App):
        return _upload(client, "dbs", "db_file", app, minifam_dcp)

    return upload


@pytest.fixture
def upload_minifam(upload_minifam_hmm, upload_minifam_db):
    def upload(client: TestClient, app: main.App):
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201

        response = upload_minifam_db(client, app)
        assert response.status_code == 201

    return upload


@pytest.fixture
def upload_pfam1_hmm():
    pfam1_hmm = data.filepath(data.FileName.pfam1_hmm)

    def upload(client: TestClient, app: main.App):
        return _upload(client, "hmms", "hmm_file", app, pfam1_hmm)

    return upload


@pytest.fixture
def upload_pfam1_db():
    pfam1_dcp = data.filepath(data.FileName.pfam1_db)

    def upload(client: TestClient, app: main.App):
        return _upload(client, "dbs", "db_file", app, pfam1_dcp)

    return upload


@pytest.fixture
def upload_pfam1(upload_pfam1_hmm, upload_pfam1_db):
    def upload(client: TestClient, app: main.App):
        response = upload_pfam1_hmm(client, app)
        assert response.status_code == 201

        response = upload_pfam1_db(client, app)
        assert response.status_code == 201

    return upload
