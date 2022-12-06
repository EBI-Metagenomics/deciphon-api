from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.utils import ID
from deciphon_api.auth import auth_request
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ScanNotFoundException
from deciphon_api.models import Prod, Scan
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

AUTH = [Depends(auth_request)]
OK = HTTP_200_OK
CREATED = HTTP_201_CREATED
BUFSIZE = 4 * 1024 * 1024


def ProdSetFile():
    return File(content_type="application/gzip", description="product set")


@router.post(
    "/scans/{scan_id}/prods/",
    response_model=Prod,
    status_code=CREATED,
    dependencies=AUTH,
)
async def upload_prodset(scan_id: int = ID(), prodset: UploadFile = ProdSetFile()):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise ScanNotFoundException()
    file = await get_depo().store_prodset(scan_id, prodset)
    pass
