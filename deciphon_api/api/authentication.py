from fastapi import Depends
from fastapi.security import APIKeyHeader

from deciphon_api.core.settings import settings

__all__ = ["auth_request"]


def auth_request(token: str = Depends(APIKeyHeader(name="X-API-Key"))) -> bool:
    authenticated = token == settings.api_key
    return authenticated
