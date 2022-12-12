from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

from anyio import open_file
from fastapi import UploadFile

from deciphon_api.bufsize import BUFSIZE
from deciphon_api.filehash import FileHash
from deciphon_api.models import DB, HMM

__all__ = ["get_depo", "Depo", "File"]


class File:
    def __init__(self, path: Path, filehash: Optional[FileHash] = None):
        self._filehash = filehash
        self._path = path.resolve()

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def xxh3_64(self) -> int:
        assert self._filehash is not None
        return self._filehash.intdigest()


class Depo:
    def __init__(self):
        self._root = Path("depo").resolve()
        self._hmms = self._root / "hmms"
        self._dbs = self._root / "dbs"
        self._prods = self._root / "prods"

        self._root.mkdir(exist_ok=True)
        self._hmms.mkdir(exist_ok=True)
        self._dbs.mkdir(exist_ok=True)
        self._prods.mkdir(exist_ok=True)

    async def _store(self, file: UploadFile, root_dir: Path) -> File:
        filehash = FileHash()
        async with await open_file(root_dir / file.filename, "wb") as f:
            while content := await file.read(BUFSIZE):
                filehash.update(content)
                await f.write(content)
        return File(root_dir / file.filename, filehash=filehash)

    async def store_hmm(self, file: UploadFile) -> File:
        return await self._store(file, self._hmms)

    async def store_db(self, file: UploadFile) -> File:
        return await self._store(file, self._dbs)

    def _fetch(self, filename: str) -> File:
        return File(path=self._root / filename)

    def fetch(self, model: Union[HMM, DB]) -> File:
        if isinstance(model, HMM):
            return File(path=self._hmms / model.filename)
        elif isinstance(model, DB):
            return File(path=self._dbs / model.filename)
        else:
            assert False


@lru_cache
def get_depo() -> Depo:
    return Depo()
