import os
import shutil

from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.job import JobPost


def test_httppost_jobs_db_notfound(app: FastAPI):
    with TestClient(app) as client:
        response = client.post("/api/jobs/", json=JobPost.example().dict())
        assert response.status_code == 404
        assert response.json() == {"rc": "einval", "msg": "database not found"}


def test_httppost_jobs(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})
        assert response.status_code == 201

        response = client.post("/api/jobs/", json=JobPost.example().dict())
        assert response.status_code == 201
        json = response.json()
        assert "submission" in json
        del json["submission"]
        assert json == {
            "db_id": 1,
            "error": "",
            "exec_ended": 0,
            "exec_started": 0,
            "hmmer3_compat": False,
            "id": 1,
            "multi_hits": True,
            "state": "pend",
        }


def test_httpget_jobs_next_pend_empty(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200
        assert response.json() == []


def test_httpget_jobs_next_pend(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})
        assert response.status_code == 201
        response = client.post("/api/jobs/", json=JobPost.example().dict())
        assert response.status_code == 201
        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200

        json = response.json()
        assert "submission" in json[0]
        del json[0]["submission"]
        assert json == [
            {
                "db_id": 1,
                "error": "",
                "exec_ended": 0,
                "exec_started": 0,
                "hmmer3_compat": False,
                "id": 1,
                "multi_hits": True,
                "state": "pend",
            },
        ]


def test_httppatch_jobs_set_run(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})
        assert response.status_code == 201
        response = client.post("/api/jobs/", json=JobPost.example().dict())
        assert response.status_code == 201
        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200

        job_id = response.json()[0]["id"]
        response = client.patch(f"/api/jobs/{job_id}", json={"state": "run", "error": ""})
        assert response.status_code == 200

        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "run"


def test_httppatch_jobs_invalid_set(app: FastAPI):
    minifam = data.filepath(data.FileName.minifam_dcp)
    shutil.copy(minifam, os.getcwd())

    with TestClient(app) as client:
        response = client.post("/api/dbs/", json={"filename": "minifam.dcp"})
        assert response.status_code == 201
        response = client.post("/api/jobs/", json=JobPost.example().dict())
        assert response.status_code == 201
        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200

        job_id = response.json()[0]["id"]
        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "fail", "error": "failed"}
        )
        assert response.status_code == 403
