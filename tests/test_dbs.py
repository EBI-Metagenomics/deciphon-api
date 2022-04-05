import cgi
import ctypes

import xxhash
from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data


def test_upload_hmm(app: FastAPI, upload_hmm):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)

    with TestClient(app) as client:
        response = upload_hmm(client, minifam_hmm)
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "xxh3": -1400478458576472411,
            "filename": "minifam.hmm",
            "job_id": 1,
        }


def test_upload_database(app: FastAPI, upload_hmm, upload_database):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)
    minifam_dcp = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_hmm(client, minifam_hmm)
        assert response.status_code == 201

        response = upload_database(client, minifam_dcp)
        assert response.status_code == 201

        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 1,
        }


def test_get_database(app: FastAPI, upload_hmm, upload_database):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)
    minifam_dcp = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_hmm(client, minifam_hmm)
        assert response.status_code == 201

        response = upload_database(client, minifam_dcp)
        assert response.status_code == 201

        response = client.get("/api/dbs/1")
        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 1,
        }


def test_get_database_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/api/dbs/1")
        assert response.status_code == 404
        assert response.json() == {
            "rc": "einval",
            "msg": "database not found",
        }


def test_download_database(app: FastAPI, upload_hmm, upload_database):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)
    minifam_dcp = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_hmm(client, minifam_hmm)
        assert response.status_code == 201

        response = upload_database(client, minifam_dcp)
        assert response.status_code == 201

        response = client.get("/api/dbs/1/download")
        assert response.status_code == 200

        attach = cgi.parse_header(response.headers["content-disposition"])
        filename = attach[1]["filename"]

        x = xxhash.xxh3_64()
        with open(filename, "wb") as f:
            for chunk in response:
                x.update(chunk)
                f.write(chunk)

        v = ctypes.c_int64(x.intdigest()).value
        assert v == -3907098992699871052


def test_download_database_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/api/dbs/1/download")
        assert response.status_code == 404
        assert response.json() == {"msg": "database not found", "rc": "einval"}


def test_get_database_list(app: FastAPI, upload_hmm, upload_database):
    minifam_hmm = data.filepath(data.FileName.minifam_hmm)
    minifam_dcp = data.filepath(data.FileName.minifam_dcp)

    pfam1_hmm = data.filepath(data.FileName.pfam1_hmm)
    pfam1_dcp = data.filepath(data.FileName.pfam1_dcp)

    with TestClient(app) as client:

        response = upload_hmm(client, minifam_hmm)
        assert response.status_code == 201

        response = upload_database(client, minifam_dcp)
        assert response.status_code == 201

        response = upload_hmm(client, pfam1_hmm)
        assert response.status_code == 201

        response = upload_database(client, pfam1_dcp)
        assert response.status_code == 201

        response = client.get("/api/dbs")
        assert response.json() == [
            {
                "id": 1,
                "xxh3": -3907098992699871052,
                "filename": "minifam.dcp",
                "hmm_id": 1,
            },
            {
                "id": 2,
                "xxh3": -1370598402004110900,
                "filename": "pfam1.dcp",
                "hmm_id": 2,
            },
        ]
