from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None


class PaginatedResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: dict[str, Any] | None = None


class SuccessResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None
