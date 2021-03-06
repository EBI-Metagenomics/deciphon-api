import pytest
from fastapi.testclient import TestClient
from upload import upload_minifam

import deciphon_api.data as data
from deciphon_api.main import app, settings
from deciphon_api.models.scan import ScanPost

api_prefix = settings.api_prefix
api_key = settings.api_key


@pytest.mark.usefixtures("cleandir")
def test_upload_products():
    with TestClient(app) as client:
        upload_minifam(client)

        response = client.post(
            f"{api_prefix}/scans/",
            json=ScanPost.example().dict(),
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 201

        response = client.get(f"{api_prefix}/jobs/next_pend")
        assert response.status_code == 200

        with open("prods_file.tsv", "wb") as f:
            f.write(data.prods_file_content().encode())

        response = client.post(
            f"{api_prefix}/prods/",
            files={
                "prods_file": (
                    "prods_file.tsv",
                    open("prods_file.tsv", "rb"),
                    "text/tab-separated-values",
                )
            },
            headers={"X-API-Key": f"{api_key}"},
        )
        assert response.status_code == 201
        assert response.json() == []
