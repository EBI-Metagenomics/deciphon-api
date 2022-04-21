from fastapi.testclient import TestClient

from deciphon_api.main import App


def test_get_not_found_hmm(app: App):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        response = client.get(f"{prefix}/hmms/1")
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}

        response = client.get(f"{prefix}/hmms/1", params={"id_type": "hmm_id"})
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}

        response = client.get(f"{prefix}/hmms/name", params={"id_type": "filename"})
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}


def test_upload_hmm(app: App, upload_minifam_hmm):
    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "xxh3": -1400478458576472411,
            "filename": "minifam.hmm",
            "job_id": 1,
        }

        response = upload_minifam_hmm(client, app)
        assert response.status_code == 418
        assert response.json() == {
            "rc": 21,
            "msg": "hmm already exists",
        }


def test_get_hmm(app: App, upload_minifam_hmm):
    prefix = app.api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }

    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms/1")
        assert response.status_code == 200
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms/1", params={"id_type": "hmm_id"})
        assert response.status_code == 200
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms/1", params={"id_type": "job_id"})
        assert response.status_code == 200
        assert response.json() == expect

        response = client.get(
            f"{prefix}/hmms/-1400478458576472411", params={"id_type": "xxh3"}
        )
        assert response.status_code == 200
        assert response.json() == expect

        response = client.get(
            f"{prefix}/hmms/minifam.hmm", params={"id_type": "filename"}
        )
        assert response.status_code == 200
        assert response.json() == expect


def test_get_list(app: App, upload_minifam_hmm):
    prefix = app.api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }

    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms")
        assert response.status_code == 200
        assert response.json() == [expect]


def test_remove_hmm(app: App, upload_minifam_hmm):
    prefix = app.api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }
    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.delete(f"{prefix}/hmms/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{app.api_key}"}
        response = client.delete(f"{prefix}/hmms/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}

        response = client.delete(f"{prefix}/hmms/1", headers=hdrs)
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}


def test_download_hmm(app: App, upload_minifam_hmm):
    prefix = app.api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }
    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms/1/download")
        assert response.status_code == 200
