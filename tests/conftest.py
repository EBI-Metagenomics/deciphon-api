import os
import shutil
import tempfile

import pytest
from fastapi import FastAPI

from deciphon_api.blob import get_blob


@pytest.fixture
def app() -> FastAPI:
    from deciphon_api.main import get_app

    return get_app()


@pytest.fixture
def cleandir():
    old_cwd = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    yield
    os.chdir(old_cwd)
    shutil.rmtree(newpath)


@pytest.fixture
def minifam_hmm():
    return get_blob("minifam.hmm")


@pytest.fixture
def minifam_dcp():
    return get_blob("minifam.dcp")


@pytest.fixture
def consensus_fna():
    return get_blob("consensus.fna")


@pytest.fixture
def pfam1_hmm():
    return get_blob("pfam1.hmm")


@pytest.fixture
def pfam1_dcp():
    return get_blob("pfam1.dcp")


@pytest.fixture
def prod_tar_gz():
    return get_blob("prod.tar.gz")
