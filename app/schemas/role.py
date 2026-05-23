from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description='角色名称')
    code: str = Field(..., min_length=2, max_length=50, description='角色代码')
    description: Optional[str] = Field(None, description='角色描述')
    permissions: dict[str, Any] = Field(default_factory=dict, description='权限配置')


class RoleCreate(RoleBase):
    is_system: bool = Field(False, description='系统内置角色')


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description='角色名称')
    description: Optional[str] = Field(None, description='角色描述')
    permissions: Optional[dict[str, Any]] = Field(None, description='权限配置')


class RoleSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_system: bool
    created_at: datetime
