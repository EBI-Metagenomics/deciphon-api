from fastapi.testclient import TestClient

from deciphon_api.main import App


def test_root(app: App):
    with TestClient(app.api) as client:
        response = client.get(app.api_prefix)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
