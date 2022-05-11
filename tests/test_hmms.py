import pytest
from fastapi.testclient import TestClient
from upload import upload_minifam_hmm

from deciphon_api.main import app, settings

api_prefix = settings.api_prefix
api_key = settings.api_key


@pytest.mark.usefixtures("cleandir")
def test_get_not_found_hmm():
    prefix = api_prefix
    with TestClient(app) as client:
        response = client.get(f"{prefix}/hmms/1")
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}

        response = client.get(f"{prefix}/hmms/1", params={"id_type": "hmm_id"})
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}

        response = client.get(f"{prefix}/hmms/name", params={"id_type": "filename"})
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}


@pytest.mark.usefixtures("cleandir")
def test_upload_hmm_no_api_key():
    with TestClient(app) as client:
        response = upload_minifam_hmm(client, False)
        assert response.status_code == 403
        assert response.json() == {"msg": "Not authenticated", "rc": 129}


@pytest.mark.usefixtures("cleandir")
def test_upload_hmm():
    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "xxh3": -1400478458576472411,
            "filename": "minifam.hmm",
            "job_id": 1,
        }

        response = upload_minifam_hmm(client)
        assert response.status_code == 418
        assert response.json() == {
            "rc": 21,
            "msg": "hmm already exists",
        }


@pytest.mark.usefixtures("cleandir")
def test_get_hmm():
    prefix = api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }

    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
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


@pytest.mark.usefixtures("cleandir")
def test_get_list():
    prefix = api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }

    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms")
        assert response.status_code == 200
        assert response.json() == [expect]


@pytest.mark.usefixtures("cleandir")
def test_remove_hmm():
    prefix = api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }
    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.delete(f"{prefix}/hmms/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{api_key}"}
        response = client.delete(f"{prefix}/hmms/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}

        response = client.delete(f"{prefix}/hmms/1", headers=hdrs)
        assert response.status_code == 404
        assert response.json() == {"rc": 2, "msg": "hmm not found"}


@pytest.mark.usefixtures("cleandir")
def test_download_hmm():
    prefix = api_prefix
    expect = {
        "id": 1,
        "xxh3": -1400478458576472411,
        "filename": "minifam.hmm",
        "job_id": 1,
    }
    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201
        assert response.json() == expect

        response = client.get(f"{prefix}/hmms/1/download")
        assert response.status_code == 200
