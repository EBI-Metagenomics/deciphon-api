import importlib.resources
from pathlib import Path

import anyblob

__all__ = ["get_blob"]


def get_blob(name: str) -> Path:
    file = importlib.resources.files("deciphon_api").joinpath("blob.sha256")
    xy = (x.strip().split() for x in file.open("r").readlines())
    registry = {name: value for value, name in xy}
    return anyblob.get(registry[name]).as_path(name)
