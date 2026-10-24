from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int   # total matching rows
    page: int    # current page (starts at 1)
    size: int    # rows per page
    pages: int   # total pages