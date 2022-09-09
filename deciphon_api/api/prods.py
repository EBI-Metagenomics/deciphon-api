from typing import List

from fastapi import APIRouter, Depends, File, Path, UploadFile
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.models.prod import Prod

router = APIRouter()


@router.get(
    "/prods/{prod_id}",
    summary="get product",
    response_model=Prod,
    status_code=HTTP_200_OK,
    responses=responses,
    name="prods:get-product",
)
async def get_product(prod_id: int = Path(..., gt=0)):
    return Prod.get(prod_id)


@router.get(
    "/prods",
    summary="get prod list",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses=responses,
    name="prods:get-prod-list",
)
async def get_prod_list():
    return Prod.get_list()


@router.post(
    "/prods/",
    summary="upload file of products",
    response_model=JSONResponse,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="prods:upload-products",
    dependencies=[Depends(auth_request)],
)
async def upload_products(
    prods_file: UploadFile = File(
        ..., content_type="text/tab-separated-values", description="file of products"
    ),
):
    prods_file.file.flush()
    Prod.add_file(prods_file.file)
    return JSONResponse({})
