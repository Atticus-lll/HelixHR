from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.pagination import PageResult, PaginationParams
from app.models import Salary
from app.repositories import SalaryRepository
from app.schemas import SalaryCreate, SalaryUpdate


class SalaryService:
    def __init__(self, session: Session):
        self.session = session
        self.salary_repo = SalaryRepository(session)

    def _calculate_net(self, base: Decimal, bonus: Decimal, deduct: Decimal, tax: Decimal, allow: Decimal) -> Decimal:
        return base + bonus + allow - deduct - tax

    def create_salary(self, salary_data: SalaryCreate, current_user_id: int) -> Salary:
        net = self._calculate_net(
            salary_data.base_salary, salary_data.bonus,
            salary_data.deductions, salary_data.tax, salary_data.allowances
        )
        salary = self.salary_repo.create(
            created_by=current_user_id,
            net_salary=net,
            **{k: v for k, v in salary_data.model_dump().items() if v is not None}
        )
        self.session.commit()
        self.session.refresh(salary)
        return salary

    def get_salary(self, salary_id: int) -> Salary:
        salary = self.salary_repo.get(salary_id)
        if not salary:
            raise NotFoundException("薪资记录不存在")
        return salary

    def list_salaries(
        self,
        pagination: PaginationParams,
        employee_id: int | None = None,
    ) -> PageResult[Salary]:
        filters = {"employee_id": employee_id} if employee_id else None
        salaries = self.salary_repo.get_multi(
            offset=pagination.offset,
            limit=pagination.limit,
            filters=filters,
            order_by="pay_month",
            order_desc=True,
        )
        total = self.salary_repo.count(filters=filters)
        return PageResult(items=salaries, total=total, page=pagination.page, page_size=pagination.page_size)

    def update_salary(self, salary_id: int, salary_data: SalaryUpdate) -> Salary:
        salary = self.salary_repo.get(salary_id)
        if not salary:
            raise NotFoundException("薪资记录不存在")
        payload = salary_data.model_dump(exclude_unset=True, exclude_none=True)
        base = payload.get("base_salary", salary.base_salary)
        bonus = payload.get("bonus", salary.bonus)
        deduct = payload.get("deductions", salary.deductions)
        tax = payload.get("tax", salary.tax)
        allow = payload.get("allowances", salary.allowances)
        payload["net_salary"] = self._calculate_net(base, bonus, deduct, tax, allow)
        salary = self.salary_repo.update(salary, **payload)
        self.session.commit()
        self.session.refresh(salary)
        return salary

    def get_employee_salary_history(
        self,
        employee_id: int,
        pagination: PaginationParams,
    ) -> PageResult[Salary]:
        salaries = self.salary_repo.get_by_employee(employee_id)
        total = len(salaries)
        start = pagination.offset
        end = start + pagination.limit
        page_items = salaries[start:end]
        return PageResult(items=page_items, total=total, page=pagination.page, page_size=pagination.page_size)
