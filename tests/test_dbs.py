import cgi
import ctypes
import os
import shutil

import xxhash
from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data


def test_httppost_dbs(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})

    assert response.status_code == 201
    assert response.json() == {
        "filename": "minifam.dcp",
        "id": 1,
        "xxh3_64": -3907098992699871052,
    }


def test_httppost_dbs_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "notfound.hmm"})
        assert response.status_code == 412
        assert response.json() == {
            "rc": "einval",
            "msg": "file not found",
        }


def test_httpget_dbs(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})
        assert response.status_code == 201

        response = client.get("/api/dbs/1")
        assert response.json() == [
            {"filename": "minifam.dcp", "id": 1, "xxh3_64": -3907098992699871052}
        ]


def test_httpget_dbs_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/api/dbs/1")
        assert response.status_code == 404
        assert response.json() == {
            "rc": "einval",
            "msg": "database not found",
        }


def test_httpget_dbs_download(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})
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
