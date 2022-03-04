from fastapi import APIRouter

from . import (
    httpget,
    httpget_dbs,
    httpget_dbs_xxx,
    httpget_dbs_xxx_download,
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
    httppost_jobs,
    httppost_prods_upload,
)

router = APIRouter()

router.include_router(httpget.router)
router.include_router(httpget_dbs.router)
router.include_router(httpget_dbs_xxx.router)
router.include_router(httpget_dbs_xxx_download.router)
router.include_router(httpget_jobs_next_pend.router)
router.include_router(httpget_jobs_xxx.router)
router.include_router(httpget_jobs_xxx_prods.router)
router.include_router(httpget_jobs_xxx_prods_fasta_yyy.router)
router.include_router(httpget_jobs_xxx_prods_gff.router)
router.include_router(httpget_jobs_xxx_seqs.router)
router.include_router(httpget_jobs_xxx_seqs_next_yyy.router)
router.include_router(httpget_prods_upload_example.router)
router.include_router(httpget_prods_xxx.router)
router.include_router(httpget_seqs_xxx.router)
router.include_router(httppatch_jobs_xxx.router)
router.include_router(httppost_dbs.router)
router.include_router(httppost_jobs.router)
router.include_router(httppost_prods_upload.router)
