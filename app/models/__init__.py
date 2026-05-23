from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

from app.models.role import Role
from app.models.user import User
from app.models.department import Dept
from app.models.employee import Employee
from app.models.salary import Salary

sys_user_role = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id"), primary_key=True),
)

__all__ = [
    "Base",
    "sys_user_role",
    "User",
    "Role",
    "Dept",
    "Employee",
    "Salary",
]
