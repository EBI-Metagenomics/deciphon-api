import pytest
from fastapi.testclient import TestClient

from deciphon_api.main import app, settings

api_prefix = settings.api_prefix
api_key = settings.api_key


@pytest.mark.usefixtures("cleandir")
def test_root():
    with TestClient(app) as client:
        response = client.get(api_prefix)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
