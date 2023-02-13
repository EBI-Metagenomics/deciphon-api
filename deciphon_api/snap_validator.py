from deciphon_api.models import SnapCreate, ProdCreate, Seq
from pathlib import Path
import csv
from typing import Union, List
from deciphon_api.snap_fs import snap_fs
from deciphon_api.errors import InvalidSnapFileError

__all__ = ["snap_validator"]


def snap_validator(scan_id: int, seqs: List[Seq], snap: SnapCreate):
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
            validate_products(scan_id, file)
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


def stringify(x: Union[bytes, str]):
    if isinstance(x, bytes):
        return x.decode()
    return x


def validate_products(scan_id: int, file):
    for row in csv.DictReader((stringify(i) for i in file), delimiter="\t"):
        assert scan_id == int(row["scan_id"])
        del row["scan_id"]
        ProdCreate.parse_obj(row)
