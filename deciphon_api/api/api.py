from fastapi import APIRouter

from deciphon_api.api import dbs, hmms, jobs, prods, scans, sched, seqs

router = APIRouter()


@router.get("/")
def httpget():
    return {"msg": "Hello World"}


router.include_router(dbs.router)
router.include_router(hmms.router)
router.include_router(jobs.router)
router.include_router(prods.router)
router.include_router(scans.router)
router.include_router(sched.router)
router.include_router(seqs.router)
