from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.core.pagination import PageResult, PaginationParams
from app.models import Employee
from app.repositories import EmployeeRepository
from app.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, session: Session):
        self.session = session
        self.emp_repo = EmployeeRepository(session)

    def create_employee(self, emp_data: EmployeeCreate, current_user_id: int) -> Employee:
        if self.emp_repo.exists(employee_number=emp_data.employee_number):
            raise ConflictException("工号已存在")
        if self.emp_repo.get_by_name(emp_data.name):
            raise ConflictException("员工姓名已存在")
        emp = self.emp_repo.create(
            created_by=current_user_id,
            **{k: v for k, v in emp_data.model_dump().items() if v is not None}
        )
        self.session.commit()
        self.session.refresh(emp)
        return emp

    def get_employee(self, emp_id: int) -> Employee:
        emp = self.emp_repo.get_with_department(emp_id)
        if not emp:
            raise NotFoundException("员工不存在")
        return emp

    def list_employees(
        self,
        pagination: PaginationParams,
        department_id: int | None = None,
        employment_status: str | None = None,
    ) -> PageResult[Employee]:
        employees = self.emp_repo.get_multi_with_department(
            offset=pagination.offset,
            limit=pagination.limit,
            department_id=department_id,
            employment_status=employment_status,
        )
        total = self.emp_repo.count()
        return PageResult(
            items=list(employees),
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    def update_employee(self, emp_id: int, emp_data: EmployeeUpdate) -> Employee:
        emp = self.emp_repo.get(emp_id)
        if not emp:
            raise NotFoundException("员工不存在")
        payload = emp_data.model_dump(exclude_unset=True, exclude_none=True)
        if "name" in payload:
            existing = self.emp_repo.get_by_name(payload["name"])
            if existing and existing.id != emp_id:
                raise ConflictException("员工姓名已存在")
        emp = self.emp_repo.update(emp, **payload)
        self.session.commit()
        self.session.refresh(emp)
        return emp

    def delete_employee(self, emp_id: int) -> None:
        emp = self.emp_repo.get(emp_id)
        if not emp:
            raise NotFoundException("员工不存在")
        self.emp_repo.delete(emp)
        self.session.commit()
