from typing import Optional

from sqlmodel import Field, SQLModel


class H3RBase(SQLModel):
    data: bytes
    prod_id: int = Field(..., gt=0, foreign_key="prod.id")


class H3R(H3RBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True, gt=0)


class H3RCreate(H3RBase):
    pass


class H3RRead(H3RBase):
    id: int
