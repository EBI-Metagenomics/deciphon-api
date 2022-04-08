from fastapi.testclient import TestClient

from deciphon_api.main import App
from deciphon_api.models.scan import ScanPost


def test_get_next_pend_job_empty(app: App):
    with TestClient(app.api) as client:
        response = client.get(f"{app.api_prefix}/jobs/next_pend")
        assert response.status_code == 200
        assert response.json() == []


def test_get_next_pend_job(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201

        response = client.get(f"{app.api_prefix}/jobs/next_pend")
        assert response.status_code == 200

        json = response.json()
        assert "submission" in json[0]
        del json[0]["submission"]

        assert json == [
            {
                "id": 1,
                "type": 1,
                "state": "pend",
                "progress": 0,
                "error": "",
                "exec_ended": 0,
                "exec_started": 0,
            },
        ]


def test_set_job_state_run(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state", json={"state": "run", "error": ""}
        )
        assert response.status_code == 200

        response = client.get(f"{app.api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "run"
        assert response.json()["error"] == ""


def test_set_job_state_run_and_fail(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state", json={"state": "run", "error": ""}
        )
        assert response.status_code == 200

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "fail", "error": "failed"},
        )
        assert response.status_code == 200

        response = client.get(f"{app.api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "fail"
        assert response.json()["error"] == "failed"


def test_set_job_state_run_and_done(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state", json={"state": "run", "error": ""}
        )
        assert response.status_code == 200

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "done", "error": ""},
        )
        assert response.status_code == 200

        response = client.get(f"{app.api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "done"
        assert response.json()["error"] == ""


def test_set_job_state_wrongly(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "invalid", "error": ""},
        )
        assert response.status_code == 422

        response = client.get(f"{app.api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "pend"
        assert response.json()["error"] == ""
