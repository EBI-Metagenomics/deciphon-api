import os
from pathlib import Path

import pytest
from fastapi import FastAPI

from deciphon_api.main import get_app


@pytest.fixture
def app(tmp_path: Path) -> FastAPI:
    os.chdir(tmp_path)
    return get_app()
