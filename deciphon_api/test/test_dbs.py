import os
import shutil
from pathlib import Path

from fastapi.testclient import TestClient


def test_httppost_dbs(tmp_path: Path):
    os.chdir(tmp_path)

    import deciphon_api.data as data
    from deciphon_api import app

    minifam = data.filepath(data.FileName.minifam)
    shutil.copy(minifam, os.getcwd())
    print(os.getcwd())

    with TestClient(app) as client:
        response = client.post("/dbs/", json={"filename": "minifam.hmm"})
        assert response.status_code == 201
        assert response.json() == {
            "filename": "minifam.hmm",
            "id": 1,
            "xxh64": -8445839449675891342,
        }
