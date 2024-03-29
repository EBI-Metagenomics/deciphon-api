import pytest
from fasta_reader import read_fasta
from fastapi.testclient import TestClient
from upload import upload_minifam

import deciphon_api.data as data
from deciphon_api.main import app, settings

api_prefix = settings.api_prefix
api_key = settings.api_key


@pytest.mark.usefixtures("cleandir")
def test_submit_scan_with_non_existent_database():
    with TestClient(app) as client:

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 404
        assert response.json() == {"rc": 4, "msg": "database not found"}


@pytest.mark.usefixtures("cleandir")
def test_submit_scan():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201

        json = response.json()
        assert "submission" in json
        del json["submission"]

        assert json == {
            "id": 2,
            "type": 0,
            "state": "pend",
            "progress": 0,
            "error": "",
            "exec_ended": 0,
            "exec_started": 0,
        }


@pytest.mark.usefixtures("cleandir")
def test_get_scan():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201

        response = client.get(f"{api_prefix}/scans/1")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "db_id": 1,
            "multi_hits": True,
            "hmmer3_compat": False,
            "job_id": 2,
        }

        response = client.get(f"{api_prefix}/scans/2")
        assert response.status_code == 404
        assert response.json() == {"rc": 3, "msg": "scan not found"}


@pytest.mark.usefixtures("cleandir")
def test_get_scan_list():
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 201

        response = client.get(f"{api_prefix}/scans")
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


@pytest.mark.usefixtures("cleandir")
def test_get_next_scan_seq():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201
        items = read_fasta(consensus_faa).read_items()

        response = client.get(f"{prefix}/scans/1/seqs/next/0")
        assert response.status_code == 200

        assert response.json() == {
            "id": 1,
            "scan_id": 1,
            "name": items[0].id,
            "data": items[0].sequence,
        }

        response = client.get(f"{prefix}/scans/1/seqs/next/1")
        assert response.status_code == 200
        assert response.json() == {
            "id": 2,
            "scan_id": 1,
            "name": items[1].id,
            "data": items[1].sequence,
        }

        response = client.get(f"{prefix}/scans/1/seqs/next/2")
        assert response.status_code == 200
        assert response.json() == {
            "id": 3,
            "scan_id": 1,
            "name": items[2].id,
            "data": items[2].sequence,
        }

        response = client.get(f"{prefix}/scans/1/seqs/next/3")
        assert response.status_code == 204


@pytest.mark.usefixtures("cleandir")
def test_get_scan_seqs():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201
        items = read_fasta(consensus_faa).read_items()

        response = client.get(f"{prefix}/scans/1/seqs")
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


@pytest.mark.usefixtures("cleandir")
def test_get_scan_prods():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

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
        assert response.json() == {}

        response = client.get(f"{prefix}/scans/1/prods")
        assert response.status_code == 200

        assert response.json() == [
            {
                "id": 1,
                "scan_id": 1,
                "seq_id": 1,
                "profile_name": "PF00742.20",
                "abc_name": "dna",
                "alt_loglik": -547.8771362304688,
                "null_loglik": -690.8677368164062,
                "profile_typeid": "protein",
                "version": "0.0.1",
                "match": ",S,,;,B,,;CCT,M1,CCT,P;ATC,M2,ATC,I;ATT,M3,ATT,I;TCG,M4,TCG,S;ACG,M5,ACG,T;CTC,M6,CTC,L;AAG,M7,AAG,K;GAG,M8,GAG,E;TCG,M9,TCG,S;CTG,M10,CTG,L;ACA,M11,ACA,T;GGT,M12,GGT,G;GAC,M13,GAC,D;CGT,M14,CGT,R;ATT,M15,ATT,I;ACT,M16,ACT,T;CGA,M17,CGA,R;ATC,M18,ATC,I;GAA,M19,GAA,E;GGG,M20,GGG,G;ATA,M21,ATA,I;TTA,M22,TTA,L;AAC,M23,AAC,N;GGC,M24,GGC,G;ACC,M25,ACC,T;CTG,M26,CTG,L;AAT,M27,AAT,N;TAC,M28,TAC,Y;ATT,M29,ATT,I;CTC,M30,CTC,L;ACT,M31,ACT,T;GAG,M32,GAG,E;ATG,M33,ATG,M;GAG,M34,GAG,E;GAA,M35,GAA,E;GAG,M36,GAG,E;GGG,M37,GGG,G;GCT,M38,GCT,A;TCA,M39,TCA,S;TTC,M40,TTC,F;TCT,M41,TCT,S;GAG,M42,GAG,E;GCG,M43,GCG,A;CTG,M44,CTG,L;AAG,M45,AAG,K;GAG,M46,GAG,E;GCA,M47,GCA,A;CAG,M48,CAG,Q;GAA,M49,GAA,E;TTG,M50,TTG,L;GGC,M51,GGC,G;TAC,M52,TAC,Y;GCG,M53,GCG,A;GAA,M54,GAA,E;GCG,M55,GCG,A;GAT,M56,GAT,D;CCT,M57,CCT,P;ACG,M58,ACG,T;GAC,M59,GAC,D;GAT,M60,GAT,D;GTG,M61,GTG,V;GAA,M62,GAA,E;GGG,M63,GGG,G;CTA,M64,CTA,L;GAT,M65,GAT,D;GCT,M66,GCT,A;GCT,M67,GCT,A;AGA,M68,AGA,R;AAG,M69,AAG,K;CTG,M70,CTG,L;GCA,M71,GCA,A;ATT,M72,ATT,I;CTA,M73,CTA,L;GCC,M74,GCC,A;AGA,M75,AGA,R;TTG,M76,TTG,L;GCA,M77,GCA,A;TTT,M78,TTT,F;GGG,M79,GGG,G;TTA,M80,TTA,L;GAG,M81,GAG,E;GTC,M82,GTC,V;GAG,M83,GAG,E;TTG,M84,TTG,L;GAG,M85,GAG,E;GAC,M86,GAC,D;GTA,M87,GTA,V;GAG,M88,GAG,E;GTG,M89,GTG,V;GAA,M90,GAA,E;GGA,M91,GGA,G;ATT,M92,ATT,I;GAA,M93,GAA,E;AAG,M94,AAG,K;CTG,M95,CTG,L;ACT,M96,ACT,T;GCC,M97,GCC,A;GAA,M98,GAA,E;GAT,M99,GAT,D;ATT,M100,ATT,I;GAA,M101,GAA,E;GAA,M102,GAA,E;GCG,M103,GCG,A;AAG,M104,AAG,K;GAA,M105,GAA,E;GAG,M106,GAG,E;GGT,M107,GGT,G;AAA,M108,AAA,K;GTT,M109,GTT,V;TTA,M110,TTA,L;AAA,M111,AAA,K;CTA,M112,CTA,L;GTG,M113,GTG,V;GCA,M114,GCA,A;AGC,M115,AGC,S;GCC,M116,GCC,A;GTC,M117,GTC,V;GAA,M118,GAA,E;GCC,M119,GCC,A;AGG,M120,AGG,R;GTC,M121,GTC,V;AAG,M122,AAG,K;CCT,M123,CCT,P;GAG,M124,GAG,E;CTG,M125,CTG,L;GTA,M126,GTA,V;CCT,M127,CCT,P;AAG,M128,AAG,K;TCA,M129,TCA,S;CAT,M130,CAT,H;CCA,M131,CCA,P;TTA,M132,TTA,L;GCC,M133,GCC,A;TCG,M134,TCG,S;GTA,M135,GTA,V;AAA,M136,AAA,K;GGC,M137,GGC,G;TCT,M138,TCT,S;GAC,M139,GAC,D;AAC,M140,AAC,N;GCC,M141,GCC,A;GTG,M142,GTG,V;GCT,M143,GCT,A;GTA,M144,GTA,V;GAA,M145,GAA,E;ACG,M146,ACG,T;GAA,M147,GAA,E;CGG,M148,CGG,R;GTA,M149,GTA,V;GGC,M150,GGC,G;GAA,M151,GAA,E;CTC,M152,CTC,L;GTA,M153,GTA,V;GTG,M154,GTG,V;CAG,M155,CAG,Q;GGA,M156,GGA,G;CCA,M157,CCA,P;GGG,M158,GGG,G;GCT,M159,GCT,A;GGC,M160,GGC,G;GCA,M161,GCA,A;GAG,M162,GAG,E;CCA,M163,CCA,P;ACC,M164,ACC,T;GCA,M165,GCA,A;TCC,M166,TCC,S;GCT,M167,GCT,A;GTA,M168,GTA,V;CTC,M169,CTC,L;GCT,M170,GCT,A;GAC,M171,GAC,D;CTT,M172,CTT,L;CTC,M173,CTC,L;,E,,;,T,,",
            },
            {
                "id": 2,
                "scan_id": 1,
                "seq_id": 2,
                "profile_name": "PF00696.29",
                "abc_name": "dna",
                "alt_loglik": -802.6513061523438,
                "null_loglik": -974.4751586914062,
                "profile_typeid": "protein",
                "version": "0.0.1",
                "match": ",S,,;,B,,;AAA,M1,AAA,K;CGT,M2,CGT,R;GTA,M3,GTA,V;GTT,M4,GTT,V;GTA,M5,GTA,V;AAG,M6,AAG,K;CTT,M7,CTT,L;GGG,M8,GGG,G;GGT,M9,GGT,G;AGT,M10,AGT,S;TCT,M11,TCT,S;CTG,M12,CTG,L;ACA,M13,ACA,T;GAT,M14,GAT,D;AAG,M15,AAG,K;GAA,M16,GAA,E;GAG,M17,GAG,E;GCA,M18,GCA,A;TCA,M19,TCA,S;CTC,M20,CTC,L;AGG,M21,AGG,R;CGT,M22,CGT,R;TTA,M23,TTA,L;GCT,M24,GCT,A;GAG,M25,GAG,E;CAG,M26,CAG,Q;ATT,M27,ATT,I;GCA,M28,GCA,A;GCA,M29,GCA,A;TTA,M30,TTA,L;AAA,M31,AAA,K;GAG,M32,GAG,E;AGT,M33,AGT,S;GGC,M34,GGC,G;AAT,M35,AAT,N;AAA,M36,AAA,K;CTA,M37,CTA,L;GTG,M38,GTG,V;GTC,M39,GTC,V;GTG,M40,GTG,V;CAT,M41,CAT,H;GGA,M42,GGA,G;GGC,M43,GGC,G;GGC,M44,GGC,G;AGC,M45,AGC,S;TTC,M46,TTC,F;ACT,M47,ACT,T;GAT,M48,GAT,D;GGT,M49,GGT,G;CTG,M50,CTG,L;CTG,M51,CTG,L;GCA,M52,GCA,A;TTG,M53,TTG,L;AAA,M54,AAA,K;AGT,M55,AGT,S;GGC,M56,GGC,G;CTG,M57,CTG,L;AGC,M58,AGC,S;TCG,M59,TCG,S;GGC,M60,GGC,G;GAA,M61,GAA,E;TTA,M62,TTA,L;GCT,M63,GCT,A;GCG,M64,GCG,A;GGG,M65,GGG,G;TTG,M66,TTG,L;AGG,M67,AGG,R;AGC,M68,AGC,S;ACG,M69,ACG,T;TTA,M70,TTA,L;GAA,M71,GAA,E;GAG,M72,GAG,E;GCC,M73,GCC,A;GGA,M74,GGA,G;GAA,M75,GAA,E;GTA,M76,GTA,V;GCG,M77,GCG,A;ACG,M78,ACG,T;AGG,M79,AGG,R;GAC,M80,GAC,D;GCC,M81,GCC,A;CTA,M82,CTA,L;GCT,M83,GCT,A;AGC,M84,AGC,S;TTA,M85,TTA,L;GGG,M86,GGG,G;GAA,M87,GAA,E;CGG,M88,CGG,R;CTT,M89,CTT,L;GTT,M90,GTT,V;GCA,M91,GCA,A;GCG,M92,GCG,A;CTG,M93,CTG,L;CTG,M94,CTG,L;GCG,M95,GCG,A;GCG,M96,GCG,A;GGT,M97,GGT,G;CTC,M98,CTC,L;CCT,M99,CCT,P;GCT,M100,GCT,A;GTA,M101,GTA,V;GGA,M102,GGA,G;CTC,M103,CTC,L;AGC,M104,AGC,S;GCC,M105,GCC,A;GCT,M106,GCT,A;GCG,M107,GCG,A;TTA,M108,TTA,L;GAT,M109,GAT,D;GCG,M110,GCG,A;ACG,M111,ACG,T;GAG,M112,GAG,E;GCG,M113,GCG,A;GGC,M114,GGC,G;CGG,M115,CGG,R;GAT,M116,GAT,D;GAA,M117,GAA,E;GGC,M118,GGC,G;AGC,M119,AGC,S;GAC,M120,GAC,D;GGG,M121,GGG,G;AAC,M122,AAC,N;GTC,M123,GTC,V;GAG,M124,GAG,E;TCC,M125,TCC,S;GTG,M126,GTG,V;GAC,M127,GAC,D;GCA,M128,GCA,A;GAA,M129,GAA,E;GCA,M130,GCA,A;ATT,M131,ATT,I;GAG,M132,GAG,E;GAG,M133,GAG,E;TTG,M134,TTG,L;CTT,M135,CTT,L;GAG,M136,GAG,E;GCC,M137,GCC,A;GGG,M138,GGG,G;GTG,M139,GTG,V;GTC,M140,GTC,V;CCC,M141,CCC,P;GTC,M142,GTC,V;CTA,M143,CTA,L;ACA,M144,ACA,T;GGA,M145,GGA,G;TTT,M146,TTT,F;ATC,M147,ATC,I;GGC,M148,GGC,G;TTA,M149,TTA,L;GAC,M150,GAC,D;GAA,M151,GAA,E;GAA,M152,GAA,E;GGG,M153,GGG,G;GAA,M154,GAA,E;CTG,M155,CTG,L;GGA,M156,GGA,G;AGG,M157,AGG,R;GGA,M158,GGA,G;TCT,M159,TCT,S;TCT,M160,TCT,S;GAC,M161,GAC,D;ACC,M162,ACC,T;ATC,M163,ATC,I;GCT,M164,GCT,A;GCG,M165,GCG,A;TTA,M166,TTA,L;CTC,M167,CTC,L;GCT,M168,GCT,A;GAA,M169,GAA,E;GCT,M170,GCT,A;TTA,M171,TTA,L;GGC,M172,GGC,G;GCG,M173,GCG,A;GAC,M174,GAC,D;AAA,M175,AAA,K;CTC,M176,CTC,L;ATA,M177,ATA,I;ATA,M178,ATA,I;CTG,M179,CTG,L;ACC,M180,ACC,T;GAC,M181,GAC,D;GTA,M182,GTA,V;GAC,M183,GAC,D;GGC,M184,GGC,G;GTT,M185,GTT,V;TAC,M186,TAC,Y;GAT,M187,GAT,D;GCC,M188,GCC,A;GAC,M189,GAC,D;CCT,M190,CCT,P;AAA,M191,AAA,K;AAG,M192,AAG,K;GTC,M193,GTC,V;CCA,M194,CCA,P;GAC,M195,GAC,D;GCG,M196,GCG,A;AGG,M197,AGG,R;CTC,M198,CTC,L;TTG,M199,TTG,L;CCA,M200,CCA,P;GAG,M201,GAG,E;ATA,M202,ATA,I;AGT,M203,AGT,S;GTG,M204,GTG,V;GAC,M205,GAC,D;GAG,M206,GAG,E;GCC,M207,GCC,A;GAG,M208,GAG,E;GAA,M209,GAA,E;AGC,M210,AGC,S;GCC,M211,GCC,A;TCC,M212,TCC,S;GAA,M213,GAA,E;TTA,M214,TTA,L;GCG,M215,GCG,A;ACC,M216,ACC,T;GGT,M217,GGT,G;GGG,M218,GGG,G;ATG,M219,ATG,M;AAG,M220,AAG,K;GTC,M221,GTC,V;AAA,M222,AAA,K;CAT,M223,CAT,H;CCA,M224,CCA,P;GCG,M225,GCG,A;GCT,M226,GCT,A;CTT,M227,CTT,L;GCT,M228,GCT,A;GCA,M229,GCA,A;GCT,M230,GCT,A;AGA,M231,AGA,R;CGG,M232,CGG,R;GGG,M233,GGG,G;GGT,M234,GGT,G;ATT,M235,ATT,I;CCG,M236,CCG,P;GTC,M237,GTC,V;GTG,M238,GTG,V;ATA,M239,ATA,I;ACG,M240,ACG,T;AAT,M241,AAT,N;,E,,;,T,,",
            },
        ]


@pytest.mark.usefixtures("cleandir")
def test_get_scan_prods_as_gff():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

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
        assert response.json() == {}

        response = client.get(f"{prefix}/scans/1/prods/gff")
        assert response.status_code == 200
        assert response.text == data.prods_as_gff_content()


@pytest.mark.usefixtures("cleandir")
def test_get_scan_prods_as_amino():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

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
        assert response.json() == {}

        response = client.get(f"{prefix}/scans/1/prods/amino")
        assert response.status_code == 200
        assert response.text == data.prods_as_amino_content()


@pytest.mark.usefixtures("cleandir")
def test_get_scan_prods_as_path():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

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
        assert response.json() == {}

        response = client.get(f"{prefix}/scans/1/prods/path")
        assert response.status_code == 200
        assert response.text == data.prods_as_path_content()


@pytest.mark.usefixtures("cleandir")
def test_get_scan_prods_as_fragment():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

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
        assert response.json() == {}

        response = client.get(f"{prefix}/scans/1/prods/fragment")
        assert response.status_code == 200
        assert response.text == data.prods_as_fragment_content()


@pytest.mark.usefixtures("cleandir")
def test_get_scan_prods_as_codon():
    prefix = api_prefix
    with TestClient(app) as client:
        upload_minifam(client)

        consensus_faa = data.filepath(data.FileName.consensus_faa)
        response = client.post(
            f"{api_prefix}/scans/",
            data={"db_id": 1, "multi_hits": True, "hmmer3_compat": False},
            files={
                "fasta_file": (
                    consensus_faa.name,
                    open(consensus_faa, "rb"),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 201

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
        assert response.json() == {}

        response = client.get(f"{prefix}/scans/1/prods/codon")
        assert response.status_code == 200
        assert response.text == data.prods_as_codon_content()
