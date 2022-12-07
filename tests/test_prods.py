from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from deciphon_api.config import get_config
from deciphon_api.mime import OCTET, TEXT

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


def test_post_prods(
    app, minifam_hmm, minifam_dcp, consensus_fna, prod_tar_gz, prod_json
):
    with TestClient(app, backend="trio") as client:
        files = files_form("hmm_file", minifam_hmm, TEXT)
        response = client.post(url("/hmms/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("db_file", minifam_dcp, OCTET)
        response = client.post(url("/dbs/"), files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("fasta_file", consensus_fna, TEXT)
        response = client.post(url("/scans/"), data=DATA, files=files, headers=HEADERS)
        assert response.status_code == 201

        files = files_form("prod_file", prod_tar_gz, OCTET)
        response = client.post(url("/scans/1/prods/"), files=files, headers=HEADERS)
        assert response.status_code == 201
        assert response.json() == prod_json


# def test_get_scan_prods_as_gff(app: FastAPI):
#     prefix = get_config().api_prefix
#     key = get_config().api_key
#     with TestClient(app, backend="trio") as client:
#         upload_minifam(client)
#
#         consensus_faa = data.filepath(data.FileName.consensus_faa)
#         response = client.post(
#             f"{prefix}/scans/",
#             data=DATA,
#             files={
#                 "fasta_file": (
#                     consensus_faa.name,
#                     open(consensus_faa, "rb"),
#                     TEXT,
#                 )
#             },
#         )
#         assert response.status_code == 201
#
#         with open("prods_file.tsv", "wb") as f:
#             f.write(data.prods_file_content().encode())
#
#         response = client.post(
#             f"{prefix}/prods/",
#             files={
#                 "prods_file": (
#                     "prods_file.tsv",
#                     open("prods_file.tsv", "rb"),
#                     "text/tab-separated-values",
#                 )
#             },
#             headers={"X-API-Key": f"{key}"},
#         )
#         assert response.status_code == 201
#         assert response.json() == {}
#
#         response = client.get(f"{prefix}/scans/1/prods/gff")
#         assert response.status_code == 200
#         assert response.text == data.prods_as_gff_content()
#
#
# def test_get_scan_prods_as_amino(app: FastAPI):
#     prefix = get_config().api_prefix
#     key = get_config().api_key
#     with TestClient(app, backend="trio") as client:
#         upload_minifam(client)
#
#         consensus_faa = data.filepath(data.FileName.consensus_faa)
#         response = client.post(
#             f"{prefix}/scans/",
#             data=DATA,
#             files={
#                 "fasta_file": (
#                     consensus_faa.name,
#                     open(consensus_faa, "rb"),
#                     TEXT,
#                 )
#             },
#         )
#         assert response.status_code == 201
#
#         with open("prods_file.tsv", "wb") as f:
#             f.write(data.prods_file_content().encode())
#
#         response = client.post(
#             f"{prefix}/prods/",
#             files={
#                 "prods_file": (
#                     "prods_file.tsv",
#                     open("prods_file.tsv", "rb"),
#                     "text/tab-separated-values",
#                 )
#             },
#             headers={"X-API-Key": f"{key}"},
#         )
#         assert response.status_code == 201
#         assert response.json() == {}
#
#         response = client.get(f"{prefix}/scans/1/prods/amino")
#         assert response.status_code == 200
#         assert response.text == data.prods_as_amino_content()
#
#
# def test_get_scan_prods_as_path(app: FastAPI):
#     prefix = get_config().api_prefix
#     key = get_config().api_key
#     with TestClient(app, backend="trio") as client:
#         upload_minifam(client)
#
#         consensus_faa = data.filepath(data.FileName.consensus_faa)
#         response = client.post(
#             f"{prefix}/scans/",
#             data=DATA,
#             files={
#                 "fasta_file": (
#                     consensus_faa.name,
#                     open(consensus_faa, "rb"),
#                     TEXT,
#                 )
#             },
#         )
#         assert response.status_code == 201
#
#         with open("prods_file.tsv", "wb") as f:
#             f.write(data.prods_file_content().encode())
#
#         response = client.post(
#             f"{prefix}/prods/",
#             files={
#                 "prods_file": (
#                     "prods_file.tsv",
#                     open("prods_file.tsv", "rb"),
#                     "text/tab-separated-values",
#                 )
#             },
#             headers={"X-API-Key": f"{key}"},
#         )
#         assert response.status_code == 201
#         assert response.json() == {}
#
#         response = client.get(f"{prefix}/scans/1/prods/path")
#         assert response.status_code == 200
#         assert response.text == data.prods_as_path_content()
#
#
# def test_get_scan_prods_as_fragment(app: FastAPI):
#     prefix = get_config().api_prefix
#     key = get_config().api_key
#     with TestClient(app, backend="trio") as client:
#         upload_minifam(client)
#
#         consensus_faa = data.filepath(data.FileName.consensus_faa)
#         response = client.post(
#             f"{prefix}/scans/",
#             data=DATA,
#             files={
#                 "fasta_file": (
#                     consensus_faa.name,
#                     open(consensus_faa, "rb"),
#                     TEXT,
#                 )
#             },
#         )
#         assert response.status_code == 201
#
#         with open("prods_file.tsv", "wb") as f:
#             f.write(data.prods_file_content().encode())
#
#         response = client.post(
#             f"{prefix}/prods/",
#             files={
#                 "prods_file": (
#                     "prods_file.tsv",
#                     open("prods_file.tsv", "rb"),
#                     "text/tab-separated-values",
#                 )
#             },
#             headers={"X-API-Key": f"{key}"},
#         )
#         assert response.status_code == 201
#         assert response.json() == {}
#
#         response = client.get(f"{prefix}/scans/1/prods/fragment")
#         assert response.status_code == 200
#         assert response.text == data.prods_as_fragment_content()
#
#
# def test_get_scan_prods_as_codon(app: FastAPI):
#     prefix = get_config().api_prefix
#     key = get_config().api_key
#     with TestClient(app, backend="trio") as client:
#         upload_minifam(client)
#
#         consensus_faa = data.filepath(data.FileName.consensus_faa)
#         response = client.post(
#             f"{prefix}/scans/",
#             data=DATA,
#             files={
#                 "fasta_file": (
#                     consensus_faa.name,
#                     open(consensus_faa, "rb"),
#                     TEXT,
#                 )
#             },
#         )
#         assert response.status_code == 201
#
#         with open("prods_file.tsv", "wb") as f:
#             f.write(data.prods_file_content().encode())
#
#         response = client.post(
#             f"{prefix}/prods/",
#             files={
#                 "prods_file": (
#                     "prods_file.tsv",
#                     open("prods_file.tsv", "rb"),
#                     "text/tab-separated-values",
#                 )
#             },
#             headers={"X-API-Key": f"{key}"},
#         )
#         assert response.status_code == 201
#         assert response.json() == {}
#
#         response = client.get(f"{prefix}/scans/1/prods/codon")
#         assert response.status_code == 200
#         assert response.text == data.prods_as_codon_content()
