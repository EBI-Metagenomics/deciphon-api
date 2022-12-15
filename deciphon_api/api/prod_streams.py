from fastapi import APIRouter, Path
from fastapi.responses import PlainTextResponse
from sqlmodel import Session
from starlette.status import HTTP_200_OK

from deciphon_api.api.utils import ID
from deciphon_api.coordinates import Viewport
from deciphon_api.exceptions import NotFoundException
from deciphon_api.models import Scan
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
PLAIN = PlainTextResponse


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/streams/{stream_stack}",
    response_class=PLAIN,
    status_code=OK,
)
async def get_prod_streams(
    scan_id: int = ID(), prod_id: int = ID(), stream_stack: str = Path()
):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        prod = scan.get_prod(prod_id)
        hmm_path = prod.hmm_path()
        viewport = Viewport(hmm_path.coord)
        hmmer_path = prod.hmmer_path(hmm_path)

        streams = []
        for x in stream_stack.split("+"):
            if x.startswith("hmm_"):
                y = x[4:]
                if y.startswith("codon"):
                    level = int(y[len("codon") :])
                    y = "codon"
                    streams.append(
                        viewport.display(getattr(hmm_path, y + "_pixels")(level))
                    )
                elif y.startswith("target"):
                    level = int(y[len("target") :])
                    y = "target"
                    streams.append(
                        viewport.display(getattr(hmm_path, y + "_pixels")(level))
                    )
                else:
                    streams.append(viewport.display(getattr(hmm_path, y + "_pixels")()))
            if x.startswith("hmmer_"):
                y = x[6:]
                streams.append(viewport.display(getattr(hmmer_path, y + "_pixels")()))

        return "\n".join(streams) + "\n"


@router.get(
    "/scans/{scan_id}/prods/{prod_id}/streams/{stream_stack}/projected-onto/hmm_hit",
    response_class=PLAIN,
    status_code=OK,
)
async def get_prod_streams_onto(
    scan_id: int = ID(), prod_id: int = ID(), stream_stack: str = Path()
):
    with Session(get_sched()) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            raise NotFoundException(Scan)
        prod = scan.get_prod(prod_id)
        hmm_path = prod.hmm_path()
        viewport = Viewport(hmm_path.coord)
        hmmer_path = prod.hmmer_path(hmm_path)
        viewport = viewport.cut(next(hmm_path.hits()).interval)

        streams = []
        for x in stream_stack.split("+"):
            if x.startswith("hmm_"):
                y = x[4:]
                if y.startswith("codon"):
                    level = int(y[len("codon") :])
                    y = "codon"
                    streams.append(
                        viewport.display(getattr(hmm_path, y + "_pixels")(level))
                    )
                elif y.startswith("target"):
                    level = int(y[len("target") :])
                    y = "target"
                    streams.append(
                        viewport.display(getattr(hmm_path, y + "_pixels")(level))
                    )
                else:
                    streams.append(viewport.display(getattr(hmm_path, y + "_pixels")()))
            if x.startswith("hmmer_"):
                y = x[6:]
                streams.append(viewport.display(getattr(hmmer_path, y + "_pixels")()))

        return "\n".join(streams) + "\n"
