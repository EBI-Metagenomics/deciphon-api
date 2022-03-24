from fastapi import FastAPI
from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.models.scan import ScanPost


def test_upload_products(app: FastAPI, upload_database):
    minifam = data.filepath(data.FileName.minifam_dcp)

    with TestClient(app) as client:
        response = upload_database(client, minifam)
        assert response.status_code == 201

        response = client.post("/api/scans/", json=ScanPost.example().dict())
        assert response.status_code == 201

        response = client.get("/api/jobs/next_pend")
        assert response.status_code == 200

        with open("prods_file.tsv", "wb") as f:
            f.write(data.prods_file().encode())

        response = client.post(
            "/api/prods/",
            files={
                "prods_file": (
                    "prods_file.tsv",
                    open("prods_file.tsv", "rb"),
                    "text/tab-separated-values",
                )
            },
        )
        assert response.status_code == 201
        assert response.json() == []
