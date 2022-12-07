from fastapi import File

import deciphon_api.mime as mime

__all__ = ["FastaFile", "DBFile", "HMMFile", "ProdFile"]


def FastaFile():
    return File(content_type=mime.TEXT, description="fasta file")


def DBFile():
    content_type = mime.OCTET
    return File(content_type=content_type, description="deciphon database")


def HMMFile():
    return File(content_type=mime.TEXT, description="hmmer database")


def ProdFile():
    return File(content_type=mime.GZIP, description="product file")
