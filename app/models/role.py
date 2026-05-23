from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    __tablename__ = "sys_role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色代码")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="角色描述")
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict, comment="权限配置")
    is_system: Mapped[bool] = mapped_column(default=False, comment="系统内置角色")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="sys_user_role",
        back_populates="roles",
    )
