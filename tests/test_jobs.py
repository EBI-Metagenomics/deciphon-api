from fastapi.testclient import TestClient

from deciphon_api.main import App
from deciphon_api.models.scan import ScanPost


def test_get_not_found_job(app: App):
    with TestClient(app.api) as client:
        response = client.get(f"{app.api_prefix}/jobs/1")
        assert response.status_code == 404
        assert response.json() == {"msg": "job not found", "rc": 5}


def test_get_next_pend_job_empty(app: App):
    with TestClient(app.api) as client:
        response = client.get(f"{app.api_prefix}/jobs/next_pend")
        assert response.status_code == 404


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
        assert "submission" in json
        del json["submission"]

        assert json == {
            "id": 1,
            "type": 1,
            "state": "pend",
            "progress": 0,
            "error": "",
            "exec_ended": 0,
            "exec_started": 0,
        }


def test_set_job_state_run(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "run", "error": ""},
            headers={"X-API-Key": f"{app.api_key}"},
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
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "run", "error": ""},
            headers={"X-API-Key": f"{app.api_key}"},
        )
        assert response.status_code == 200

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "fail", "error": "failed"},
            headers={"X-API-Key": f"{app.api_key}"},
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
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "run", "error": ""},
            headers={"X-API-Key": f"{app.api_key}"},
        )
        assert response.status_code == 200

        response = client.patch(
            f"{app.api_prefix}/jobs/{job_id}/state",
            json={"state": "done", "error": ""},
            headers={"X-API-Key": f"{app.api_key}"},
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
            headers={"X-API-Key": f"{app.api_key}"},
        )
        assert response.status_code == 422

        response = client.get(f"{app.api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "pend"
        assert response.json()["error"] == ""


def test_get_job_list(app: App, upload_minifam, upload_pfam1):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        upload_minifam(client, app)
        upload_pfam1(client, app)

        response = client.post(f"{prefix}/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201

        response = client.get(f"{app.api_prefix}/jobs")
        assert response.status_code == 200
        data = response.json().copy()
        for v in data:
            v["submission"] = 0
        assert data == [
            {
                "id": 1,
                "type": 1,
                "state": "pend",
                "progress": 0,
                "error": "",
                "submission": 0,
                "exec_started": 0,
                "exec_ended": 0,
            },
            {
                "id": 2,
                "type": 1,
                "state": "pend",
                "progress": 0,
                "error": "",
                "submission": 0,
                "exec_started": 0,
                "exec_ended": 0,
            },
            {
                "id": 3,
                "type": 0,
                "state": "pend",
                "progress": 0,
                "error": "",
                "submission": 0,
                "exec_started": 0,
                "exec_ended": 0,
            },
        ]


def test_get_hmm_from_job(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.get(f"{app.api_prefix}/jobs/1/hmm")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "xxh3": -1400478458576472411,
            "filename": "minifam.hmm",
            "job_id": 1,
        }


def test_get_scan_from_job(app: App, upload_minifam):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        upload_minifam(client, app)
        response = client.post(f"{prefix}/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201

        response = client.get(f"{app.api_prefix}/jobs/2/scan")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "db_id": 1,
            "multi_hits": True,
            "hmmer3_compat": False,
            "job_id": 2,
        }


def test_remove_job(app: App, upload_minifam):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.delete(f"{prefix}/dbs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{app.api_key}"}
        response = client.delete(f"{prefix}/dbs/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}

        response = client.delete(f"{prefix}/dbs/1", headers=hdrs)
        assert response.status_code == 404
        assert response.json() == {"rc": 4, "msg": "database not found"}

        response = client.delete(f"{prefix}/jobs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{app.api_key}"}
        response = client.delete(f"{prefix}/jobs/1", headers=hdrs)
        assert response.status_code == 418
        assert response.json() == {"rc": 25, "msg": "failed to evaluate sql statememt"}

        response = client.delete(f"{prefix}/hmms/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}

        response = client.delete(f"{prefix}/jobs/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}

        response = client.delete(f"{prefix}/jobs/1", headers=hdrs)
        assert response.status_code == 404
        assert response.json() == {"rc": 5, "msg": "job not found"}


def test_add_job_progress(app: App, upload_minifam):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.delete(f"{prefix}/dbs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{app.api_key}"}
        response = client.patch(
            f"{prefix}/jobs/1/progress", json={"increment": 10}, headers=hdrs
        )
        assert response.status_code == 200
        data = response.json()
        del data["submission"]
        assert data == {
            "id": 1,
            "type": 1,
            "state": "pend",
            "progress": 10,
            "error": "",
            "exec_started": 0,
            "exec_ended": 0,
        }

        response = client.patch(
            f"{prefix}/jobs/1/progress", json={"increment": 100}, headers=hdrs
        )
        assert response.status_code == 200
        data = response.json()
        del data["submission"]
        assert data == {
            "id": 1,
            "type": 1,
            "state": "pend",
            "progress": 100,
            "error": "",
            "exec_started": 0,
            "exec_ended": 0,
        }
