from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.models.scan import ScanPost


def test_submit_scan_with_non_existent_database(app: FastAPI):
    with TestClient(app) as client:
        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 404
        assert response.json() == {"rc": "einval", "msg": "database not found"}


def test_submit_scan(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201

        json = response.json()
        assert "submission" in json
        del json["submission"]

        assert json == {
            "id": 1,
            "type": 0,
            "state": "pend",
            "progress": 0,
            "error": "",
            "exec_ended": 0,
            "exec_started": 0,
        }