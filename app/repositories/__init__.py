from app.repositories.base import BaseRepository
from app.repositories.user_repo import UserRepository
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.department_repo import DepartmentRepository
from app.repositories.salary_repo import SalaryRepository
from app.repositories.role_repo import RoleRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "EmployeeRepository",
    "DepartmentRepository",
    "SalaryRepository",
    "RoleRepository",
]
