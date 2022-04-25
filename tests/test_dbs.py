import cgi
import ctypes

import pytest
import xxhash
from fastapi.testclient import TestClient
from upload import upload_minifam, upload_minifam_db, upload_minifam_hmm, upload_pfam1

from deciphon_api.main import app, settings

api_prefix = settings.api_prefix
api_key = settings.api_key


@pytest.mark.usefixtures("cleandir")
def test_upload_database():
    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201

        response = upload_minifam_db(client)
        assert response.status_code == 201

        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 1,
        }


@pytest.mark.usefixtures("cleandir")
def test_get_database():
    expect = {
        "id": 1,
        "xxh3": -3907098992699871052,
        "filename": "minifam.dcp",
        "hmm_id": 1,
    }

    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201

        response = upload_minifam_db(client)
        assert response.status_code == 201

        response = client.get(api_prefix + "/dbs/1")
        assert response.status_code == 200
        assert response.json() == expect

        params = {"id_type": "db_id"}
        response = client.get(api_prefix + "/dbs/1", params=params)
        assert response.status_code == 200
        assert response.json() == expect

        params = {"id_type": "xxh3"}
        response = client.get(api_prefix + "/dbs/-3907098992699871052", params=params)
        assert response.status_code == 200
        assert response.json() == expect

        params = {"id_type": "filename"}
        response = client.get(api_prefix + "/dbs/minifam.dcp", params=params)
        assert response.status_code == 200
        assert response.json() == expect

        params = {"id_type": "hmm_id"}
        response = client.get(api_prefix + "/dbs/1", params=params)
        assert response.status_code == 200
        assert response.json() == expect


@pytest.mark.usefixtures("cleandir")
def test_get_database_notfound():
    with TestClient(app) as client:
        response = client.get(api_prefix + "/dbs/1")
        assert response.status_code == 404
        assert response.json() == {
            "rc": 4,
            "msg": "database not found",
        }


@pytest.mark.usefixtures("cleandir")
def test_download_database():
    with TestClient(app) as client:
        response = upload_minifam_hmm(client)
        assert response.status_code == 201

        response = upload_minifam_db(client)
        assert response.status_code == 201

        response = client.get(api_prefix + "/dbs/1/download")
        assert response.status_code == 200

        attach = cgi.parse_header(response.headers["content-disposition"])
        filename = attach[1]["filename"]

        x = xxhash.xxh3_64()
        with open(filename, "wb") as f:
            for chunk in response:
                x.update(chunk)
                f.write(chunk)

        v = ctypes.c_int64(x.intdigest()).value
        assert v == -3907098992699871052


@pytest.mark.usefixtures("cleandir")
def test_download_database_notfound():
    with TestClient(app) as client:
        response = client.get(api_prefix + "/dbs/1/download")
        assert response.status_code == 404
        assert response.json() == {"msg": "database not found", "rc": 4}


@pytest.mark.usefixtures("cleandir")
def test_get_database_list():
    with TestClient(app) as client:

        upload_minifam(client)

        upload_pfam1(client)

        response = client.get(api_prefix + "/dbs")
        assert response.json() == [
            {
                "id": 1,
                "xxh3": -3907098992699871052,
                "filename": "minifam.dcp",
                "hmm_id": 1,
            },
            {
                "id": 2,
                "xxh3": -1370598402004110900,
                "filename": "pfam1.dcp",
                "hmm_id": 2,
            },
        ]


@pytest.mark.usefixtures("cleandir")
def test_remove_database():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        response = client.delete(f"{prefix}/dbs/1")
        assert response.status_code == 403

        hdrs = {"X-API-Key": f"{api_key}"}
        response = client.delete(f"{prefix}/dbs/1", headers=hdrs)
        assert response.status_code == 200
        assert response.json() == {}
