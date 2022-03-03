from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ..examples import prods_file

router = APIRouter()


@router.get("/prods/upload/example", response_class=PlainTextResponse)
def httpget_prods_upload_example():
    return prods_file
