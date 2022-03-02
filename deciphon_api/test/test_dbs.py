from fastapi.testclient import TestClient

from deciphon_api import app

client = TestClient(app)


def test_httppost_dbs():
    response = client.post("/dbs/", json=["filename", "minifam.hmm"])
    # ?filename=pfam24.dcp
    assert response.status_code == 500
    assert response.json() == {"msg": "Hello World"}
