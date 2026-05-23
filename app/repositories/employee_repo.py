from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    model = Employee

    def get_with_department(self, emp_id: int) -> Employee | None:
        return self.session.scalar(
            select(Employee).options(joinedload(Employee.department)).where(Employee.id == emp_id)
        )

    def get_multi_with_department(
        self,
        offset: int = 0,
        limit: int = 10,
        department_id: int | None = None,
        employment_status: str | None = None,
    ) -> list[Employee]:
        stmt = select(Employee).options(joinedload(Employee.department))
        if department_id:
            stmt = stmt.where(Employee.department_id == department_id)
        if employment_status:
            stmt = stmt.where(Employee.employment_status == employment_status)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.scalars(stmt).all())

    def count_by_department(self, department_id: int) -> int:
        return self.session.scalar(
            select(func.count()).select_from(Employee).where(Employee.department_id == department_id)
        ) or 0

    def get_by_employee_number(self, employee_number: str) -> Employee | None:
        return self.session.scalar(
            select(Employee).where(Employee.employee_number == employee_number)
        )

    def get_by_name(self, name: str) -> Employee | None:
        return self.session.scalar(select(Employee).where(Employee.name == name))
