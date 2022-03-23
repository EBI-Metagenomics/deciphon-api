from fastapi import APIRouter

from deciphon_api.api import dbs, jobs, scans, seqs, wipe

router = APIRouter()


@router.get("/")
def httpget():
    return {"msg": "Hello World"}


router.include_router(dbs.router)
router.include_router(jobs.router)
router.include_router(scans.router)
router.include_router(seqs.router)
router.include_router(wipe.router)
