import ctypes

import xxhash

__all__ = ["FileHash"]


class FileHash:
    def __init__(self):
        self._xxh3_64 = xxhash.xxh3_64()

    def update(self, data: bytes):
        self._xxh3_64.update(data)

    def intdigest(self) -> int:
        return ctypes.c_int64(self._xxh3_64.intdigest()).value
