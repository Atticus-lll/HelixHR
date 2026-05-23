from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Salary
from app.repositories.base import BaseRepository


class SalaryRepository(BaseRepository[Salary]):
    model = Salary

    def get_by_employee(self, employee_id: int) -> list[Salary]:
        return list(self.session.scalars(
            select(Salary).where(Salary.employee_id == employee_id).order_by(Salary.pay_month.desc())
        ).all())

    def get_by_employee_and_month(self, employee_id: int, pay_month) -> Salary | None:
        return self.session.scalar(
            select(Salary).where(Salary.employee_id == employee_id, Salary.pay_month == pay_month)
        )
