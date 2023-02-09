from fastapi import Path

__all__ = ["IDPath"]


def IDPath():
    return Path(..., gt=0)
