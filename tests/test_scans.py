from pathlib import Path

import pytest
from fasta_reader import read_fasta
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deciphon_api.config import get_config

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("cleandir")]
HEADERS = {"X-API-Key": f"{get_config().api_key}"}
DATA = {"db_id": "1", "multi_hits": "True", "hmmer3_compat": "False"}


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


def test_db_not_found(app: FastAPI, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(
            url("/scans/"),
            data=DATA,
            files=files,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "DB not found"}


def test_submit(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        json = response.json()
        assert "submission" in json
        del json["submission"]

        assert json == {
            "id": 2,
            "type": "scan",
            "state": "pend",
            "progress": 0,
            "error": None,
            "exec_ended": None,
            "exec_started": None,
        }


def test_get(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1"))
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "db_id": 1,
            "multi_hits": True,
            "hmmer3_compat": False,
            "job_id": 2,
        }

        response = client.get(url("/scans/2"))
        assert response.status_code == 404
        assert response.json() == {"detail": "Scan not found"}


def test_get_list(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans"))
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 1,
                "db_id": 1,
                "multi_hits": True,
                "hmmer3_compat": False,
                "job_id": 2,
            }
        ]


def test_get_next_seq(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        response = client.get(url("/scans/1/seqs/next/0"))
        assert response.status_code == 200

        items = read_fasta(consensus_fna).read_items()
        assert response.json() == {
            "id": 1,
            "scan_id": 1,
            "name": items[0].id,
            "data": items[0].sequence,
        }

        response = client.get(url("/scans/1/seqs/next/1"))
        assert response.status_code == 200
        assert response.json() == {
            "id": 2,
            "scan_id": 1,
            "name": items[1].id,
            "data": items[1].sequence,
        }

        response = client.get(url("/scans/1/seqs/next/2"))
        assert response.status_code == 200
        assert response.json() == {
            "id": 3,
            "scan_id": 1,
            "name": items[2].id,
            "data": items[2].sequence,
        }

        response = client.get(url("/scans/1/seqs/next/3"))
        assert response.status_code == 404


def test_get_seqs(app: FastAPI, minifam_hmm, minifam_dcp, consensus_fna):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, "text/plain")
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, "application/octet-stream")
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, "text/plain")
        response = client.post(url("/scans/"), data=DATA, files=files)
        assert response.status_code == 201
        items = read_fasta(consensus_fna).read_items()

        response = client.get(url("/scans/1/seqs"))
        assert response.status_code == 200

        assert response.json() == [
            {
                "id": 1,
                "scan_id": 1,
                "name": items[0].id,
                "data": items[0].sequence,
            },
            {
                "id": 2,
                "scan_id": 1,
                "name": items[1].id,
                "data": items[1].sequence,
            },
            {
                "id": 3,
                "scan_id": 1,
                "name": items[2].id,
                "data": items[2].sequence,
            },
        ]
