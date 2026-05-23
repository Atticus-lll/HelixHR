from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='用户名')
    email: Optional[str] = Field(None, description='邮箱')
    full_name: Optional[str] = Field(None, max_length=100, description='姓名')


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description='密码')
    role_ids: list[int] = Field(default_factory=list, description='角色ID列表')


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, description='邮箱')
    full_name: Optional[str] = Field(None, max_length=100, description='姓名')
    is_active: Optional[bool] = Field(None, description='是否激活')
    role_ids: Optional[list[int]] = Field(None, description='角色ID列表')


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: list['RoleSimple'] = Field(default_factory=list)


class UserSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: Optional[str] = None


class RoleSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
