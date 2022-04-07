from fastapi.testclient import TestClient

from deciphon_api.main import App
from deciphon_api.models.scan import ScanPost


def test_submit_scan_with_non_existent_database(app: App):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        response = client.post(f"{prefix}/scans/", json=ScanPost.example().dict())
        assert response.status_code == 404
        assert response.json() == {"rc": "einval", "msg": "database not found"}


def test_submit_scan(app: App, upload_minifam):
    prefix = app.api_prefix
    with TestClient(app.api) as client:
        upload_minifam(client, prefix)

        response = client.post(f"{prefix}/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201

        json = response.json()
        assert "submission" in json
        del json["submission"]

        assert json == {
            "id": 2,
            "type": 0,
            "state": "pend",
            "progress": 0,
            "error": "",
            "exec_ended": 0,
            "exec_started": 0,
        }
