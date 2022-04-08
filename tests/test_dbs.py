import cgi
import ctypes

import xxhash
from fastapi.testclient import TestClient

from deciphon_api.main import App


def test_upload_database(app: App, upload_minifam_hmm, upload_minifam_db):
    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201

        response = upload_minifam_db(client, app)
        assert response.status_code == 201

        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 1,
        }


def test_get_database(app: App, upload_minifam_hmm, upload_minifam_db):
    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201

        response = upload_minifam_db(client, app)
        assert response.status_code == 201

        response = client.get(app.api_prefix + "/dbs/1")
        assert response.json() == {
            "id": 1,
            "xxh3": -3907098992699871052,
            "filename": "minifam.dcp",
            "hmm_id": 1,
        }


def test_get_database_notfound(app: App):
    with TestClient(app.api) as client:
        response = client.get(app.api_prefix + "/dbs/1")
        assert response.status_code == 404
        assert response.json() == {
            "rc": "einval",
            "msg": "database not found",
        }


def test_download_database(app: App, upload_minifam_hmm, upload_minifam_db):
    with TestClient(app.api) as client:
        response = upload_minifam_hmm(client, app)
        assert response.status_code == 201

        response = upload_minifam_db(client, app)
        assert response.status_code == 201

        response = client.get(app.api_prefix + "/dbs/1/download")
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


def test_download_database_notfound(app: App):
    with TestClient(app.api) as client:
        response = client.get(app.api_prefix + "/dbs/1/download")
        assert response.status_code == 404
        assert response.json() == {"msg": "database not found", "rc": "einval"}


def test_get_database_list(app: App, upload_minifam, upload_pfam1):
    with TestClient(app.api) as client:

        upload_minifam(client, app)

        upload_pfam1(client, app)

        response = client.get(app.api_prefix + "/dbs")
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
