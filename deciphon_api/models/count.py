from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["Count"]


class Count(BaseModel):
    count: int = Field(..., ge=0)
