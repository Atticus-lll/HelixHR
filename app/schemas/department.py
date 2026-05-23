from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeptBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description='部门名称')
    code: str = Field(..., min_length=2, max_length=20, description='部门编码')
    parent_id: Optional[int] = Field(None, description='父部门ID')
    manager_id: Optional[int] = Field(None, description='部门负责人ID')
    description: Optional[str] = Field(None, description='部门描述')


class DeptCreate(DeptBase):
    pass


class DeptUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description='部门名称')
    parent_id: Optional[int] = Field(None, description='父部门ID')
    manager_id: Optional[int] = Field(None, description='部门负责人ID')
    description: Optional[str] = Field(None, description='部门描述')


class DeptResponse(DeptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    employee_count: Optional[int] = Field(None, description='员工数量')


class DeptSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
