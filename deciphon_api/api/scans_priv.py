import tempfile

import sqlalchemy.exc
from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session
from starlette.status import HTTP_201_CREATED

from deciphon_api.api.files import ProdFile
from deciphon_api.api.utils import AUTH, ID
from deciphon_api.bufsize import BUFSIZE
from deciphon_api.depo import get_depo
from deciphon_api.exceptions import ConflictException, NotFoundException
from deciphon_api.models import JobState, Prod, Scan
from deciphon_api.prodfile import ProdFileReader
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

CREATED = HTTP_201_CREATED


def get_session():
    with Session(get_sched()) as session:
        yield session


@router.post(
    "/scans/{scan_id}/prods/",
    response_model=list[Prod],
    status_code=CREATED,
    dependencies=AUTH,
)
async def upload_prod(
    scan_id: int = ID(),
    prod_file: UploadFile = ProdFile(),
    session: Session = Depends(get_session),
):

    with tempfile.NamedTemporaryFile("wb") as file:
        while content := await prod_file.read(BUFSIZE):
            file.write(content)
        file.flush()

        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)

        scan.job.state = JobState.done
        scan.job.progress = 100

        prod_reader = ProdFileReader(file.name)
        match_file = prod_reader.match_file()
        for match in match_file.read_records():
            assert match.scan_id == scan_id
            hmmer_blob = prod_reader.hmmer_blob(match.seq_id, match.profile)
            assert hmmer_blob is not None
            depo = get_depo()
            sha256_hexdigest = await depo.store_blob(hmmer_blob)
            prod = Prod(**match.dict(), hmmer_sha256=sha256_hexdigest)
            scan.prods.append(prod)
            session.add(prod)
            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                raise ConflictException(str(e.orig))
        session.refresh(scan)
        return scan.prods
