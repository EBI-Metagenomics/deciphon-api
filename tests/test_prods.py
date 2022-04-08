from fastapi.testclient import TestClient

import deciphon_api.data as data
from deciphon_api.main import App
from deciphon_api.models.scan import ScanPost


def test_upload_products(app: App, upload_minifam):
    with TestClient(app.api) as client:
        upload_minifam(client, app)

        response = client.post(
            f"{app.api_prefix}/scans/", json=ScanPost.example().dict()
        )
        assert response.status_code == 201

        response = client.get(f"{app.api_prefix}/jobs/next_pend")
        assert response.status_code == 200

        with open("prods_file.tsv", "wb") as f:
            f.write(data.prods_file_content().encode())

        response = client.post(
            f"{app.api_prefix}/prods/",
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
