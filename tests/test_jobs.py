from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deciphon_api.config import get_config

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("cleandir")]
HEADERS = {"X-API-Key": f"{get_config().api_key}"}
DATA = {"db_id": "1", "multi_hits": "True", "hmmer3_compat": "False"}


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


def test_not_found(app: FastAPI):
    with TestClient(app, backend="trio") as client:
        response = client.get("/jobs/1")
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}


def test_empty_next_pend(app: FastAPI):
    with TestClient(app, backend="trio") as client:
        response = client.get("/jobs/next-pend")
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}


def test_next_pend(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get("/jobs/next-pend")
        assert response.status_code == 200

        json = response.json()
        assert "submission" in json
        del json["submission"]

        assert json == {
            "id": 1,
            "type": "hmm",
            "state": "pend",
            "progress": 0,
            "error": None,
            "exec_ended": None,
            "exec_started": None,
        }


def test_set_run(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            url(f"/jobs/{job_id}/state"),
            params={"state": "run", "error": None},
            headers=HEADERS,
        )
        assert response.status_code == 200

        response = client.get(url(f"/jobs/{job_id}"))
        assert response.status_code == 200
        assert response.json()["state"] == "run"
        assert response.json()["error"] == ""


def test_set_run_and_fail(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            url(f"/jobs/{job_id}/state"),
            params={"state": "run", "error": None},
            headers=HEADERS,
        )
        assert response.status_code == 200
        response = client.get(url(f"/jobs/{job_id}"))
        assert response.status_code == 200
        assert response.json()["state"] == "run"
        assert response.json()["error"] == ""

        response = client.patch(
            url(f"/jobs/{job_id}/state"),
            params={"state": "fail", "error": "failed"},
            headers=HEADERS,
        )
        assert response.status_code == 200
        response = client.get(url(f"/jobs/{job_id}"))
        assert response.status_code == 200
        assert response.json()["state"] == "fail"
        assert response.json()["error"] == "failed"


def test_set_run_and_done(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            url(f"/jobs/{job_id}/state"),
            params={"state": "run", "error": None},
            headers=HEADERS,
        )
        assert response.status_code == 200
        response = client.get(url(f"/jobs/{job_id}"))
        assert response.status_code == 200
        assert response.json()["state"] == "run"
        assert response.json()["error"] == ""

        response = client.patch(
            url(f"/jobs/{job_id}/state"),
            params={"state": "done", "error": None},
            headers=HEADERS,
        )
        assert response.status_code == 200
        response = client.get(url(f"/jobs/{job_id}"))
        assert response.status_code == 200
        assert response.json()["state"] == "done"
        assert response.json()["error"] == ""


def test_get_list(
    app: FastAPI, minifam_hmm, minifam_dcp, pfam1_hmm, pfam1_dcp, consensus_fna
):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("hmm_file", pfam1_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", pfam1_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get("/jobs")
        assert response.status_code == 200
        jdata = response.json().copy()
        for v in jdata:
            del v["submission"]
        assert jdata == [
            {
                "id": 1,
                "type": "hmm",
                "state": "pend",
                "progress": 0,
                "error": None,
                "exec_started": None,
                "exec_ended": None,
            },
            {
                "id": 2,
                "type": "hmm",
                "state": "pend",
                "progress": 0,
                "error": None,
                "exec_started": None,
                "exec_ended": None,
            },
            {
                "id": 3,
                "type": "scan",
                "state": "pend",
                "progress": 0,
                "error": None,
                "exec_started": None,
                "exec_ended": None,
            },
        ]


def test_get_hmm_from_job(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)

        response = client.get("/jobs/1/hmm")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "xxh3": -1400478458576472411,
            "filename": "minifam.hmm",
            "job_id": 1,
        }


def test_get_scan_from_job(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get("/jobs/2/scan")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "db_id": 1,
            "multi_hits": True,
            "hmmer3_compat": False,
            "job_id": 2,
        }


def test_remove_job(app: FastAPI, minifam_hmm, minifam_dcp):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.delete(url("/dbs/1"))
        assert response.status_code == 403

        response = client.delete(url("/dbs/1"), headers=HEADERS)
        assert response.status_code == 204

        response = client.delete(url("/dbs/1"), headers=HEADERS)
        assert response.status_code == 404
        assert response.json() == {"detail": "DB not found"}

        response = client.delete(url("/jobs/1"))
        assert response.status_code == 403

        response = client.delete(url("/jobs/1"), headers=HEADERS)
        assert response.status_code == 409

        response = client.delete(url("/hmms/1"), headers=HEADERS)
        assert response.status_code == 204

        response = client.delete(url("/jobs/1"), headers=HEADERS)
        assert response.status_code == 204

        response = client.delete(url("/jobs/1"), headers=HEADERS)
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}


def test_add_job_progress(app: FastAPI, minifam_hmm):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)

        response = client.delete(url("/dbs/1"))
        assert response.status_code == 403

        response = client.patch(url("/jobs/1/progress/increment/10"), headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        del data["submission"]
        assert data == {
            "id": 1,
            "type": "hmm",
            "state": "pend",
            "progress": 10,
            "error": None,
            "exec_started": None,
            "exec_ended": None,
        }

        response = client.patch(url("/jobs/1/progress/increment/100"), headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        del data["submission"]
        assert data == {
            "id": 1,
            "type": "hmm",
            "state": "pend",
            "progress": 100,
            "error": None,
            "exec_started": None,
            "exec_ended": None,
        }
