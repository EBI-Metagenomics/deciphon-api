from pathlib import Path

from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.main import settings


def _upload(
    client: TestClient,
    file_type: str,
    file_field: str,
    path: Path,
):
    api_prefix = settings.api_prefix
    api_key = settings.api_key
    return client.post(
        f"{api_prefix}/{file_type}/",
        files={
            file_field: (
                path.name,
                open(path, "rb"),
                "application/octet-stream",
            )
        },
        headers={"X-API-Key": f"{api_key}"},
    )


def upload_minifam_hmm(client: TestClient):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)
    return _upload(client, "hmms", "hmm_file", minifam_hmm)


def upload_minifam_db(client: TestClient):
    minifam_dcp = data.filepath(data.FileName.minifam_db)
    return _upload(client, "dbs", "db_file", minifam_dcp)


def upload_minifam(client: TestClient):
    response = upload_minifam_hmm(client)
    assert response.status_code == 201
    response = upload_minifam_db(client)
    assert response.status_code == 201


def upload_pfam1_hmm(client: TestClient):
    pfam1_hmm = data.filepath(data.FileName.pfam1_hmm)
    return _upload(client, "hmms", "hmm_file", pfam1_hmm)


def upload_pfam1_db(client: TestClient):
    pfam1_dcp = data.filepath(data.FileName.pfam1_db)
    return _upload(client, "dbs", "db_file", pfam1_dcp)


def upload_pfam1(client: TestClient):
    response = upload_pfam1_hmm(client)
    assert response.status_code == 201

    response = upload_pfam1_db(client)
    assert response.status_code == 201
