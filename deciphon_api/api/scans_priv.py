import tempfile

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.utils import ID
from deciphon_api.auth import auth_request
from deciphon_api.exceptions import ScanNotFoundException
from deciphon_api.models import Prod, Scan
from deciphon_api.prodfile import ProdFileReader
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

AUTH = [Depends(auth_request)]
OK = HTTP_200_OK
CREATED = HTTP_201_CREATED
BUFSIZE = 4 * 1024 * 1024


def ProdFile():
    return File(content_type="application/gzip", description="product set")


def get_session():
    with Session(get_sched()) as session:
        yield session


@router.post(
    "/scans/{scan_id}/prods/",
    response_model=list[Prod],
    status_code=CREATED,
    dependencies=AUTH,
)
async def upload_product(
    scan_id: int = ID(),
    prod_file: UploadFile = ProdFile(),
    session: Session = Depends(get_session),
):

    prods: list[Prod] = []
    with tempfile.NamedTemporaryFile("wb") as file:
        while content := await prod_file.read(BUFSIZE):
            file.write(content)
        file.flush()

        scan = session.get(Scan, scan_id)
        if not scan:
            raise ScanNotFoundException()

        prod_reader = ProdFileReader(file.name)
        match_file = prod_reader.match_file()
        for match in match_file.read_records():
            assert match.scan_id == scan_id
            hmmer_file = prod_reader.hmmer_file(match.seq_id, match.profile)
            assert hmmer_file is not None
            prod = Prod(match=match, hmmer=hmmer_file.hmmer())
            session.add(prod)
            session.commit()
            session.refresh(prod)
            prods.append(prod)
        return prods
