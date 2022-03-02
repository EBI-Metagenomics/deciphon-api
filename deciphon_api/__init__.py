from . import (
    httpget_dbs,
    httpget_dbs_xxx,
    httpget_jobs_next_pend,
    httpget_jobs_xxx,
    httpget_jobs_xxx_prods,
    httpget_jobs_xxx_prods_fasta_yyy,
    httpget_jobs_xxx_prods_gff,
    httpget_jobs_xxx_seqs,
    httpget_jobs_xxx_seqs_next_yyy,
    httpget_prods_upload_example,
    httpget_prods_xxx,
    httpget_seqs_xxx,
    httppatch_jobs_xxx,
    httppost_dbs,
    httppost_prods_upload,
)
from ._app import app
from ._version import version as __version__

__name__ = "deciphon_api"

__all__ = [
    "__name__",
    "__version__",
    "app",
    "httpget_dbs",
    "httpget_dbs_xxx",
    "httpget_jobs_next_pend",
    "httpget_jobs_xxx",
    "httpget_jobs_xxx_prods",
    "httpget_jobs_xxx_prods_fasta_yyy",
    "httpget_jobs_xxx_prods_gff",
    "httpget_jobs_xxx_seqs",
    "httpget_jobs_xxx_seqs_next_yyy",
    "httpget_prods_upload_example",
    "httpget_prods_xxx",
    "httpget_seqs_xxx",
    "httppatch_jobs_xxx",
    "httppost_dbs",
    "httppost_prods_upload",
]


@app.get("/")
def read_root():
    return {"Hello": "World"}
