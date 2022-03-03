import os
import shutil

from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data


def test_httppost_dbs(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/dbs/", json={"filename": "minifam.hmm"})
        assert response.status_code == 201
        assert response.json() == {
            "filename": "minifam.hmm",
            "id": 1,
            "xxh64": -8445839449675891342,
        }


def test_httppost_dbs_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.post("/dbs/", json={"filename": "notfound.hmm"})
        assert response.status_code == 412
        assert response.json() == {
            "rc": "einval",
            "msg": "file not found",
        }
