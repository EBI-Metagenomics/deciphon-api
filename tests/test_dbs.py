import cgi
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deciphon_api.config import get_config
from deciphon_api.filehash import FileHash
from deciphon_api.mime import OCTET, TEXT

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("cleandir")]
HEADERS = {"X-API-Key": f"{get_config().api_key}"}
EXPECT = {"id": 1, "xxh3": -3907098992699871052, "filename": "minifam.dcp", "hmm_id": 1}
BACKEND = "asyncio"


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


def test_no_access(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(
            url("/hmms/"),
            json={
                "filename": "minifam.hmm",
                "hexsha256": (
                    "fe305d9c09e123f987f49b9056e34c"
                    + "374e085d8831f815cc73d8ea4cdec84960"
                ),
            },
            headers=HEADERS,
        )
        # response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files)
        assert response.status_code == 403
        assert response.json() == {"detail": "Not authenticated"}


def test_not_found(app: FastAPI):
    with TestClient(app, backend=BACKEND) as client:
        response = client.get(url("/dbs/1"))
        assert response.status_code == 404
        assert response.json() == {"detail": "DB not found"}


def test_upload(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        assert response.json() == EXPECT

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 409


def test_get(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.get(url("/dbs/1"))
        assert response.status_code == 200
        assert response.json() == EXPECT

        xxh3 = "-3907098992699871052"
        response = client.get(url(f"/dbs/xxh3/{xxh3}"))
        assert response.status_code == 200
        assert response.json() == EXPECT

        response = client.get(url("/dbs/filename/minifam.dcp"))
        assert response.status_code == 200
        assert response.json() == EXPECT


def test_list(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.get(url("/dbs"))
        assert response.status_code == 200
        assert response.json() == [EXPECT]


def test_remove(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.delete(url("/dbs/1"))
        assert response.status_code == 403

        response = client.delete(url("/dbs/1"), headers=HEADERS)
        assert response.status_code == 204

        response = client.delete(url("/dbs/1"), headers=HEADERS)
        assert response.status_code == 404
        assert response.json() == {"detail": "DB not found"}


def test_download(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == EXPECT

        response = client.get(url("/dbs/1/download"))
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
