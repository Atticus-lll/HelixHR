from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    employee_number: str = Field(..., min_length=1, max_length=20, description='工号')
    name: str = Field(..., min_length=1, max_length=100, description='姓名')
    email: Optional[str] = Field(None, max_length=100, description='邮箱')
    phone: Optional[str] = Field(None, max_length=20, description='手机号')
    id_card: Optional[str] = Field(None, max_length=18, description='身份证号')
    gender: Optional[str] = Field(None, description='性别: 男/女/其他')
    birth_date: Optional[date] = Field(None, description='出生日期')
    hire_date: Optional[date] = Field(None, description='入职日期')
    department_id: Optional[int] = Field(None, description='部门ID')
    position: Optional[str] = Field(None, max_length=100, description='职位')
    employment_status: Optional[str] = Field('active', description='在职状态')
    address: Optional[str] = Field(None, max_length=255, description='住址')
    emergency_contact: Optional[str] = Field(None, max_length=100, description='紧急联系人')
    emergency_phone: Optional[str] = Field(None, max_length=20, description='紧急联系电话')


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description='姓名')
    email: Optional[str] = Field(None, max_length=100, description='邮箱')
    phone: Optional[str] = Field(None, max_length=20, description='手机号')
    id_card: Optional[str] = Field(None, max_length=18, description='身份证号')
    gender: Optional[str] = Field(None, description='性别')
    birth_date: Optional[date] = Field(None, description='出生日期')
    hire_date: Optional[date] = Field(None, description='入职日期')
    department_id: Optional[int] = Field(None, description='部门ID')
    position: Optional[str] = Field(None, max_length=100, description='职位')
    employment_status: Optional[str] = Field(None, description='在职状态')
    address: Optional[str] = Field(None, max_length=255, description='住址')
    emergency_contact: Optional[str] = Field(None, max_length=100, description='紧急联系人')
    emergency_phone: Optional[str] = Field(None, max_length=20, description='紧急联系电话')


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_name: Optional[str] = Field(None, description='部门名称')
    created_at: datetime
    updated_at: Optional[datetime] = None
