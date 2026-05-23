from typing import Generic, TypeVar
from math import ceil

T = TypeVar("T")


class PageResult(Generic[T]):
    def __init__(self, items: list[T], total: int, page: int, page_size: int):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.total_pages = ceil(total / page_size) if page_size > 0 else 0

    def to_dict(self) -> dict:
        items_out = []
        for item in self.items:
            if hasattr(item, "model_dump"):
                items_out.append(item.model_dump())
            elif hasattr(item, "__dict__"):
                items_out.append(item.__dict__)
            else:
                items_out.append(item)
        return {
            "items": items_out,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
        }


class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ):
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = "desc" if sort_order.lower() == "desc" else "asc"

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size
