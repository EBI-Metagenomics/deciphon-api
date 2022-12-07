from fastapi import Depends, Path

from deciphon_api.auth import auth_request

__all__ = ["ID", "AUTH"]

AUTH = [Depends(auth_request)]


def ID():
    return Path(..., gt=0)
