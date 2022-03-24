import os
import shutil

from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.models.scan import ScanPost


def test_get_next_pend_job_empty(app: FastAPI):
    with TestClient(app) as client:
        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200
        assert response.json() == []


def test_get_next_pend_job(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201

        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200

        json = response.json()
        assert "submission" in json[0]
        del json[0]["submission"]

        assert json == [
            {
                "id": 1,
                "type": 0,
                "state": "pend",
                "progress": 0,
                "error": "",
                "exec_ended": 0,
                "exec_started": 0,
            },
        ]


def test_set_job_state_run(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "run", "error": ""}
        )
        assert response.status_code == 200

        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "run"
        assert response.json()["error"] == ""


def test_set_job_state_run_and_fail(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "run", "error": ""}
        )
        assert response.status_code == 200

        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "fail", "error": "failed"}
        )
        assert response.status_code == 200

        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "fail"
        assert response.json()["error"] == "failed"


def test_set_job_state_run_and_done(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "run", "error": ""}
        )
        assert response.status_code == 200

        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "done", "error": ""}
        )
        assert response.status_code == 200

        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "done"
        assert response.json()["error"] == ""


def test_set_job_state_wrongly(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"/api/jobs/{job_id}", json={"state": "invalid", "error": ""}
        )
        assert response.status_code == 422

        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "pend"
        assert response.json()["error"] == ""
