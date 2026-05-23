from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.role import Role


class User(Base):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True, comment="邮箱")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="姓名")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="超级管理员")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.now, onupdate=datetime.now, nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="sys_user_role",
        back_populates="users",
    )

    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, permission: str) -> bool:
        if self.is_superuser:
            return True
        for role in self.roles:
            perms = role.permissions or {}
            if perms.get(permission, False) or perms.get("*", False):
                return True
        return False
