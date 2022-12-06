from fastapi import APIRouter, Depends, File,  UploadFile
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.auth import auth_request
from deciphon_api.depo import get_depo
from deciphon_api.models import Prod
from deciphon_api.sched import get_sched

__all__ = ["router"]

router = APIRouter()

AUTH = [Depends(auth_request)]
OK = HTTP_200_OK
CREATED = HTTP_201_CREATED

# @router.get(
#     "/prods/{prod_id}",
#     response_model=Prod,
#     status_code=OK,
# )
# async def get_product(prod_id: int = ID()):
#     return Prod.get(prod_id)


# @router.get(
#     "/prods",
#     response_model=list[Prod],
#     status_code=OK,
# )
# async def get_prod_list():
#     return Prod.get_list()
#


def ProdSetFile():
    return File(content_type="application/gzip", description="product set")


@router.post("/prods/", response_model=Prod, status_code=CREATED, dependencies=AUTH)
async def upload_products(prodset_file: UploadFile = ProdSetFile()):
    file = await get_depo().store_prodset(prodset_file)
    pass

    # async with aiofiles.open(prods_file.filename, "wb") as file:
    #     while content := await prods_file.read(4 * 1024 * 1024):
    #         await file.write(content)
    #
    # Prod.add_file(prods_file.filename)
    # return JSONResponse({}, HTTP_201_CREATED)
