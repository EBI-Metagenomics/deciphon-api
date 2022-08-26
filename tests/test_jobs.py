import pytest
from fastapi.testclient import TestClient
from upload import upload_minifam, upload_pfam1

import deciphon_api.data as data
from deciphon_api.main import app, settings

api_prefix = settings.api_prefix
api_key = settings.api_key


@pytest.mark.usefixtures("cleandir")
def test_get_not_found_job():
    with TestClient(app) as client:
        response = client.get(f"{api_prefix}/jobs/1")
        assert response.status_code == 404
        assert response.json() == {"msg": "job not found", "rc": 5}


@pytest.mark.usefixtures("cleandir")
def test_get_next_pend_job_empty():
    with TestClient(app) as client:
        response = client.get(f"{api_prefix}/jobs/next_pend")
        assert response.status_code == 204


@pytest.mark.usefixtures("cleandir")
def test_get_next_pend_job():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201

        response = client.get(f"{api_prefix}/jobs/next_pend")
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


@pytest.mark.usefixtures("cleandir")
def test_set_job_state_run():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{api_prefix}/jobs/{job_id}/state",
            json={"state": "run", "error": ""},
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 200

        response = client.get(f"{api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "run"
        assert response.json()["error"] == ""


@pytest.mark.usefixtures("cleandir")
def test_set_job_state_run_and_fail():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{api_prefix}/jobs/{job_id}/state",
            json={"state": "run", "error": ""},
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 200

        response = client.patch(
            f"{api_prefix}/jobs/{job_id}/state",
            json={"state": "fail", "error": "failed"},
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 200

        response = client.get(f"{api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "fail"
        assert response.json()["error"] == "failed"


@pytest.mark.usefixtures("cleandir")
def test_set_job_state_run_and_done():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{api_prefix}/jobs/{job_id}/state",
            json={"state": "run", "error": ""},
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 200

        response = client.patch(
            f"{api_prefix}/jobs/{job_id}/state",
            json={"state": "done", "error": ""},
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 200

        response = client.get(f"{api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "done"
        assert response.json()["error"] == ""


@pytest.mark.usefixtures("cleandir")
def test_set_job_state_wrongly():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201
        job_id = response.json()["id"]

        response = client.patch(
            f"{api_prefix}/jobs/{job_id}/state",
            json={"state": "invalid", "error": ""},
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 422

        response = client.get(f"{api_prefix}/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["state"] == "pend"
        assert response.json()["error"] == ""


@pytest.mark.usefixtures("cleandir")
def test_get_job_list():
    with TestClient(app) as client:
        upload_minifam(client)
        upload_pfam1(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201

        response = client.get(f"{api_prefix}/jobs")
        assert response.status_code == 200
        jdata = response.json().copy()
        for v in jdata:
            v["submission"] = 0
        assert jdata == [
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


@pytest.mark.usefixtures("cleandir")
def test_get_hmm_from_job():
    with TestClient(app) as client:
        upload_minifam(client)

        response = client.get(f"{api_prefix}/jobs/1/hmm")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "xxh3": -1400478458576472411,
            "filename": "minifam.hmm",
            "job_id": 1,
        }


@pytest.mark.usefixtures("cleandir")
def test_get_scan_from_job():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

        response = client.get(f"{api_prefix}/jobs/2/scan")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "db_id": 1,
            "multi_hits": True,
            "hmmer3_compat": False,
            "job_id": 2,
        }


@pytest.mark.usefixtures("cleandir")
def test_remove_job():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        response = client.delete(f"{prefix}/dbs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{api_key}"}
        response = client.delete(f"{prefix}/dbs/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}

        response = client.delete(f"{prefix}/dbs/1", headers=hdrs)
        assert response.status_code == 404
        assert response.json() == {"rc": 4, "msg": "database not found"}

        response = client.delete(f"{prefix}/jobs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{api_key}"}
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


@pytest.mark.usefixtures("cleandir")
def test_add_job_progress():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        response = client.delete(f"{prefix}/dbs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{api_key}"}
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
