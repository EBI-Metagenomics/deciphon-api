import cgi
import ctypes
from pathlib import Path

import xxhash
from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data


def test_upload_database(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 0,
        }


# def test_upload_database_notfound(app: FastAPI):
#     with TestClient(app) as client:
#         response = client.post("/api/dbs/", json={"filename": "notfound.hmm"})
#         assert response.status_code == 404
#         assert response.json() == {
#             "rc": "einval",
#             "msg": "file not found",
#         }


def test_get_database(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.get("/api/dbs/1")
        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 0,
        }


def test_get_database_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/api/dbs/1")
        assert response.status_code == 404
        assert response.json() == {
            "rc": "einval",
            "msg": "database not found",
        }


def test_download_database(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
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


def test_get_database_list(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)
    pfam1 = data.filepath(data.FileName.pfam1_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = upload_database(client, pfam1)
        assert response.status_code == 201

        response = client.get("/api/dbs")
        assert response.json() == [
            {
                "id": 1,
                "xxh3": -3907098992699871052,
                "filename": "minifam.dcp",
                "hmm_id": 0,
            },
            {
                "id": 2,
                "xxh3": -1370598402004110900,
                "filename": "pfam1.dcp",
                "hmm_id": 0,
            },
        ]
