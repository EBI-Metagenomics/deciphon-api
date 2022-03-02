from enum import Enum
from pathlib import Path

import pooch

from ._name import name as __name__
from ._version import version as __version__

__all__ = ["FileName", "filepath"]

GOODBOY = pooch.create(
    path=pooch.os_cache(__name__),
    base_url="https://deciphon.s3.eu-west-2.amazonaws.com/",
    version=__version__,
    version_dev="main",
    registry={"minifam.hmm.bz2": "md5:6e102264a59e7bf538ce08b9ad2b46d8"},
)


class FileName(Enum):
    minifam = "minifam.hmm"


def filepath(file_name: FileName) -> Path:
    name = f"{file_name.value}.bz2"
    fp = GOODBOY.fetch(name, processor=pooch.Decompress("bzip2", file_name.value))
    return Path(fp)
