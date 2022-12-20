from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from deciphon_api.config import get_config
from deciphon_api.mime import OCTET, TEXT

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("cleandir")]
HEADERS = {"X-API-Key": f"{get_config().api_key}"}
DATA = {"db_id": "1", "multi_hits": "True", "hmmer3_compat": "False"}
BACKEND = "asyncio"


def url(path: str):
    return f"{get_config().api_prefix}{path}"


def files_form(field: str, filepath: Path, mime: str):
    return {
        field: (
            filepath.name,
            open(filepath, "rb"),
            mime,
        )
    }


def test_post_prods(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_json
):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(
            url("/scans/fasta/"), data=DATA, files=files, headers=HEADERS
        )
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == prod_json


def test_get_scan_prods_as_gff(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_gff
):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(
            url("/scans/fasta/"), data=DATA, files=files, headers=HEADERS
        )
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1/prods/gff"))
        assert response.status_code == 200
        assert response.text == prod_gff


def test_get_scan_prods_as_amino(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_amino
):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(
            url("/scans/fasta/"), data=DATA, files=files, headers=HEADERS
        )
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1/prods/amino"))
        assert response.status_code == 200
        assert response.text == prod_amino


def test_get_scan_prods_as_codon(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_codon
):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(
            url("/scans/fasta/"), data=DATA, files=files, headers=HEADERS
        )
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1/prods/codon"))
        assert response.status_code == 200
        assert response.text == prod_codon


def test_get_scan_prods_as_query(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_query
):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(
            url("/scans/fasta/"), data=DATA, files=files, headers=HEADERS
        )
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1/prods/query"))
        assert response.status_code == 200
        assert response.text == prod_query


def test_get_scan_prods_as_path(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_path
):
    with TestClient(app, backend=BACKEND) as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(
            url("/scans/fasta/"), data=DATA, files=files, headers=HEADERS
        )
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1/prods/path"))
        assert response.status_code == 200
        assert response.text == prod_path
