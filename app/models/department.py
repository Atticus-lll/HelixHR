from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class Dept(Base):
    __tablename__ = "sys_department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True, comment="部门编码")
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sys_department.id"), nullable=True, comment="父部门ID"
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sys_user.id"), nullable=True, comment="部门负责人"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="部门描述")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=True
    )

    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department")
