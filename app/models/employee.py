from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.department import Dept


class Employee(Base):
    __tablename__ = "sys_employee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True, comment="工号"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="姓名")
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="手机号")
    id_card: Mapped[Optional[str]] = mapped_column(String(18), nullable=True, comment="身份证号")
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="性别")
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="出生日期")
    hire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="入职日期")
    department_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sys_department.id"), nullable=True, comment="部门ID"
    )
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="职位")
    employment_status: Mapped[Optional[str]] = mapped_column(
        String(20), default="active", comment="在职状态"
    )
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="住址")
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="紧急联系人")
    emergency_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="紧急联系电话")
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="创建人ID")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=True
    )

    department: Mapped[Optional["Dept"]] = relationship("Dept", back_populates="employees")
