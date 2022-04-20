import os
from typing import List

from fastapi import APIRouter, Depends, File, Path, UploadFile
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from deciphon_api.api.authentication import auth_request
from deciphon_api.api.responses import responses
from deciphon_api.core.errors import UnauthorizedError
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
def get_product(prod_id: int = Path(..., gt=0)):
    return Prod.get(prod_id)


@router.get(
    "/prods",
    summary="get prod list",
    response_model=List[Prod],
    status_code=HTTP_200_OK,
    responses=responses,
    name="prods:get-prod-list",
)
def get_prod_list():
    return Prod.get_list()


@router.post(
    "/prods/",
    summary="upload file of products",
    response_model=List,
    status_code=HTTP_201_CREATED,
    responses=responses,
    name="prods:upload-products",
)
def upload_products(
    prods_file: UploadFile = File(
        ..., content_type="text/tab-separated-values", description="file of products"
    ),
    authenticated: bool = Depends(auth_request),
):
    if not authenticated:
        raise UnauthorizedError()

    prods_file.file.flush()
    Prod.add_file(prods_file.file)
    return []
