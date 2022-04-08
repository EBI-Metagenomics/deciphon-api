from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from deciphon_api.core.settings import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

__all__ = ["auth_request"]


def auth_request(token: str = Depends(oauth2_scheme)) -> bool:
    settings = get_settings()
    authenticated = token == settings.api_key
    return authenticated
