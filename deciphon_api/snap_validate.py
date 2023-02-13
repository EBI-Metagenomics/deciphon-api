from pathlib import Path
from typing import List

from deciphon_api.errors import InvalidSnapFileError
from deciphon_api.models import Seq, SnapCreate
from deciphon_api.read_products import read_products
from deciphon_api.snap_fs import snap_fs

__all__ = ["snap_validate"]


def snap_validate(scan_id: int, seqs: List[Seq], snap: SnapCreate):
    fs = snap_fs(snap.sha256)
    if not fs.isdir("snap"):
        raise InvalidSnapFileError(snap.sha256)

    if not fs.isdir("snap/hmmer"):
        raise InvalidSnapFileError(snap.sha256)

    if not fs.isfile("snap/products.tsv"):
        raise InvalidSnapFileError(snap.sha256)

    if len(fs.ls("snap")) != 2:
        raise InvalidSnapFileError(snap.sha256)

    with fs.open("snap/products.tsv", "rb") as file:
        try:
            read_products(scan_id, file)
        except Exception:
            raise InvalidSnapFileError(snap.sha256)

    seq_ids = set([i.id for i in seqs])
    if len(seq_ids) != len(fs.ls("snap/hmmer")):
        raise InvalidSnapFileError(snap.sha256)

    for i in fs.ls("snap/hmmer"):
        try:
            seq_ids.remove(int(Path(i).name))
        except KeyError:
            raise InvalidSnapFileError(snap.sha256)
