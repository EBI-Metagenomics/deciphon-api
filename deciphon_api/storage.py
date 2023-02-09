from blx.cid import CID
from blx.client import get_client as get_blx

__all__ = ["storage_has"]


def storage_has(sha256: str) -> bool:
    return get_blx().has(CID(sha256))
