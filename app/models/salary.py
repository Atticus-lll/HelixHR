from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class Salary(Base):
    __tablename__ = "sys_salary"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sys_employee.id"), nullable=False, index=True, comment="员工ID"
    )
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), comment="基本工资")
    bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), comment="奖金")
    deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), comment="扣除")
    tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), comment="税金")
    allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), comment="补贴")
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), comment="实发工资")
    pay_month: Mapped[date] = mapped_column(Date, nullable=False, index=True, comment="薪资月份")
    payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="发放日期")
    payment_status: Mapped[str] = mapped_column(
        String(20), default="pending", comment="发放状态"
    )
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="创建人ID")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=True
    )
