import os
import tarfile
from dataclasses import dataclass, field
from typing import IO

from fsspec.implementations.libarchive import LibArchiveFileSystem

PathLike = str | bytes | os.PathLike


@dataclass
class HMMERResult:
    seq_id: int
    profile: str


def isint(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False
    return True


def check_names(members: list[tarfile.TarInfo]):
    dirs = [i.name for i in members if i.isdir()]
    files = [i.name for i in members if i.isfile()]

    try:
        dirs.remove("prod")
    except ValueError:
        raise ValueError("prod directory not found")

    try:
        files.remove("prod/matchset.tsv")
    except ValueError:
        raise ValueError("matchset.tsv file not found")

    try:
        dirs.remove("prod/hmmer")
    except ValueError:
        pass

    for dirname in dirs:
        dirsplit = dirname.split("/", 2)
        ok = len(dirsplit) == 3
        ok = ok and dirsplit[0] == "prod"
        ok = ok and dirsplit[1] == "hmmer"
        ok = ok and isint(dirsplit[2])

        if not ok:
            raise ValueError(f"{dirname} path is not valid")

    del dirs

    for file in files:
        filesplit = file.split("/", 3)
        ok = len(filesplit) == 4
        ok = ok and filesplit[0] == "prod"
        ok = ok and filesplit[1] == "hmmer"
        ok = ok and isint(filesplit[2])
        ok = ok and len(filesplit[3]) > 4
        ok = ok and filesplit[3].endswith(".h3r")
        if not ok:
            raise ValueError(f"{file} path is not valid")


header_names = [
    "scan_id",
    "seq_id",
    "profile_name",
    "abc_name",
    "alt_loglik",
    "null_loglik",
    "profile_typeid",
    "version",
    "match",
]


class ProdFile:
    def __init__(self, name: PathLike):
        with tarfile.open(name, mode="r:gz") as tar:
            check_names(list(tar.getmembers()))

        self._fs = LibArchiveFileSystem(str(name), compression="gzip")

    def open_matchset(self):
        return self._fs.open("prod/matchset.tsv", "r")

    def hmmer_files(self):
        return list(self._fs.glob("prod/hmmer/*/*.h3r"))

        # header = str(f.readline()).strip()
        # if header.split("\t") != header_names:
        #     raise ValueError("Invalid matchset header")
        #
        # for line in fs.open("prod/matchset.tsv", "r").readlines():
        #     values = str(line).strip().split("\t")
        #     if len(values) != len(header_names):
        #         raise ValueError("Invalid matchset line")
        #
        # for filepath in fs.glob("prod/hmmer/*/*.h3r"):
        #     print(filepath)

        # for i in tar.getmembers():
        #     if i.isdir():
        #         assert i.name == "prodset"
        #         r.found_dir = True
        #     elif i.isfile() and i.name == "prodset/prods.tsv":
        #         r.found_prods = True
        #     elif i.isfile():
        #         assert i.name.startswith("prodset/") == True
        #         name = i.name.replace("prodset/", "", 1)
        #
        #         fields = name.split("_", 2)
        #         assert len(fields) == 3
        #         try:
        #             scan_id = int(fields[0])
        #             seq_id = int(fields[1])
        #         except ValueError:
        #             print("Could not parse ID from file name")
        #             continue
        #
        #         profile_ext = fields[2]
        #         assert profile_ext.endswith(".h3c") == True
        #
        #         profile = profile_ext[:-4]
        #
        #         r.h3c_items.append(H3CItem(scan_id, seq_id, profile))
        #
        # pass

    # found_dir: bool = False
    # found_prods: bool = False
    # h3c_items: list[H3CItem] = field(default_factory=list)


ProdFile("prod.tar.gz")

# file = ProdFile("prodset.tar.gz")
# tar = tarfile.open("prodset.tar.gz", "r:gz")
# tarfile.open()
#
# members = [member for member in tar.getmembers()]
# r = Result()
#
# for m in members:
#     if m.isdir():
#         assert m.name == "prodset"
#         r.found_dir = True
#     elif m.isfile() and m.name == "prodset/prods.tsv":
#         r.found_prods = True
#     elif m.isfile():
#         assert m.name.startswith("prodset/") == True
#         name = m.name.replace("prodset/", "", 1)
#
#         fields = name.split("_", 2)
#         assert len(fields) == 3
#         try:
#             scan_id = int(fields[0])
#             seq_id = int(fields[1])
#         except ValueError:
#             print("Could not parse ID from file name")
#             continue
#
#         profile_ext = fields[2]
#         assert profile_ext.endswith(".h3c") == True
#
#         profile = profile_ext[:-4]
#
#         r.h3c_items.append(H3CItem(scan_id, seq_id, profile))
#
# print(r)
# # assert m1.name == "prodset/1_2_12PF00696.29.h3c"
