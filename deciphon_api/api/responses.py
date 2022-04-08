from typing import Dict, Type, Union

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.core.errors import ErrorResponse

__all__ = ["responses"]

responses: Dict[Union[int, str], Dict[str, Type[ErrorResponse]]] = {
    HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    HTTP_409_CONFLICT: {"model": ErrorResponse},
    HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
    HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}
