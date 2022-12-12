from fastapi import APIRouter
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH
from deciphon_api.models import DB, HMM, Job, Prod, Scan, Seq
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

NO_CONTENT = HTTP_204_NO_CONTENT


@router.delete("/wipe", status_code=NO_CONTENT, dependencies=AUTH)
async def wipe():
    with Session(get_sched()) as session:
        for model in [DB, HMM, Job, Prod, Scan, Seq]:
            session.query(model).delete()
            session.commit()
