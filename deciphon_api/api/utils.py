from fastapi import Path

__all__ = ["ID"]


def ID():
    return Path(..., gt=0)
