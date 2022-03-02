from fastapi.responses import PlainTextResponse

from ._app import app
from .examples import prods_file


@app.get("/prods/upload/example", response_class=PlainTextResponse)
def httpget_prods_upload_example():
    return prods_file
