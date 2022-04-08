from fastapi.testclient import TestClient

from deciphon_api.main import App


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
