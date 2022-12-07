import cgi
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deciphon_api.config import get_config
from deciphon_api.filehash import FileHash
from deciphon_api.mime import TEXT

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("cleandir")]
HEADERS = {"X-API-Key": f"{get_config().api_key}"}
EXPECT = {"id": 1, "xxh3": -1400478458576472411, "filename": "minifam.hmm", "job_id": 1}


def url(path: str):
    return f"{get_config().api_prefix}{path}"


def files_form(field: str, filepath: Path, mime: str):
    return {
        field: (
            filepath.name,
            open(filepath, "rb"),
            mime,
        )
    }


def test_no_access(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files)
        assert response.status_code == 403
        assert response.json() == {"detail": "Not authenticated"}


def test_not_found(app: FastAPI):
    with TestClient(app, backend="trio") as client:
        response = client.get(url("/hmms/1"))
        assert response.status_code == 404
        assert response.json() == {"detail": "HMM not found"}

        response = client.get(url("/hmms/xxh3/2982"))
        assert response.status_code == 404
        assert response.json() == {"detail": "HMM not found"}

        response = client.get(url("/hmms/filename/name"))
        assert response.status_code == 404
        assert response.json() == {"detail": "HMM not found"}


def test_upload(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 409


def test_get(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.get(url("/hmms/1"))
        assert response.status_code == 200
        assert response.json() == EXPECT

        xxh3 = "-1400478458576472411"
        response = client.get(url(f"/hmms/xxh3/{xxh3}"))
        assert response.status_code == 200
        assert response.json() == EXPECT

        response = client.get(url("/hmms/filename/minifam.hmm"))
        assert response.status_code == 200
        assert response.json() == EXPECT


def test_list(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.get(url("/hmms"))
        assert response.status_code == 200
        assert response.json() == [EXPECT]


def test_remove(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.delete(url("/hmms/1"))
        assert response.status_code == 403

        response = client.delete(url("/hmms/1"), headers=HEADERS)
        assert response.status_code == 204

        response = client.delete(url("/hmms/1"), headers=HEADERS)
        assert response.status_code == 404
        assert response.json() == {"detail": "HMM not found"}


def test_download(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.get(url("/hmms/1/download"))
        assert response.status_code == 200

        content_disposition = cgi.parse_header(response.headers["content-disposition"])
        filename = content_disposition[1]["filename"]
        assert filename == EXPECT["filename"]

        filehash = FileHash()
        with open(filename, "wb") as file:
            for chunk in response.iter_bytes():
                filehash.update(chunk)
                file.write(chunk)
        assert filehash.intdigest() == EXPECT["xxh3"]
