from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SalaryBase(BaseModel):
    employee_id: int = Field(..., description='员工ID')
    base_salary: Decimal = Field(Decimal('0.00'), ge=0, description='基本工资')
    bonus: Decimal = Field(Decimal('0.00'), ge=0, description='奖金')
    deductions: Decimal = Field(Decimal('0.00'), ge=0, description='扣除')
    tax: Decimal = Field(Decimal('0.00'), ge=0, description='税金')
    allowances: Decimal = Field(Decimal('0.00'), ge=0, description='补贴')
    pay_month: date = Field(..., description='薪资月份')
    payment_date: Optional[date] = Field(None, description='发放日期')
    payment_status: str = Field('pending', description='发放状态: 待发放/已发放/发放失败')


class SalaryCreate(SalaryBase):
    pass


class SalaryUpdate(BaseModel):
    base_salary: Optional[Decimal] = Field(None, ge=0, description='基本工资')
    bonus: Optional[Decimal] = Field(None, ge=0, description='奖金')
    deductions: Optional[Decimal] = Field(None, ge=0, description='扣除')
    tax: Optional[Decimal] = Field(None, ge=0, description='税金')
    allowances: Optional[Decimal] = Field(None, ge=0, description='补贴')
    payment_date: Optional[date] = Field(None, description='发放日期')
    payment_status: Optional[str] = Field(None, description='发放状态')


class SalaryResponse(SalaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    net_salary: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
