from __future__ import annotations

from enum import Enum

__all__ = ["RC"]


class RC(int, Enum):
    API_VALIDATION_ERROR = 128
    API_HTTP_ERROR = 129
