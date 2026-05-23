from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.core.pagination import PageResult, PaginationParams
from app.models import Dept
from app.repositories import DepartmentRepository, EmployeeRepository
from app.schemas import DeptCreate, DeptUpdate


class DepartmentService:
    def __init__(self, session: Session):
        self.session = session
        self.dept_repo = DepartmentRepository(session)
        self.emp_repo = EmployeeRepository(session)

    def create_department(self, dept_data: DeptCreate) -> Dept:
        if self.dept_repo.exists(name=dept_data.name):
            raise ConflictException("部门名称已存在")
        if self.dept_repo.get_by_code(dept_data.code):
            raise ConflictException("部门编码已存在")
        dept = self.dept_repo.create(
            **{k: v for k, v in dept_data.model_dump().items() if v is not None}
        )
        self.session.commit()
        self.session.refresh(dept)
        return dept

    def get_department(self, dept_id: int) -> Dept:
        dept = self.dept_repo.get(dept_id)
        if not dept:
            raise NotFoundException("部门不存在")
        return dept

    def list_departments(self, pagination: PaginationParams) -> PageResult[Dept]:
        depts = self.dept_repo.get_multi(
            offset=pagination.offset,
            limit=pagination.limit,
            order_by="created_at",
            order_desc=True,
        )
        total = self.dept_repo.count()
        return PageResult(items=depts, total=total, page=pagination.page, page_size=pagination.page_size)

    def update_department(self, dept_id: int, dept_data: DeptUpdate) -> Dept:
        dept = self.dept_repo.get(dept_id)
        if not dept:
            raise NotFoundException("部门不存在")
        payload = dept_data.model_dump(exclude_unset=True, exclude_none=True)
        if "name" in payload:
            existing = self.dept_repo.get_by_name(payload["name"])
            if existing and existing.id != dept_id:
                raise ConflictException("部门名称已存在")
        dept = self.dept_repo.update(dept, **payload)
        self.session.commit()
        self.session.refresh(dept)
        return dept

    def delete_department(self, dept_id: int) -> None:
        dept = self.dept_repo.get(dept_id)
        if not dept:
            raise NotFoundException("部门不存在")
        emp_count = self.emp_repo.count_by_department(dept_id)
        if emp_count > 0:
            raise ConflictException("该部门下有 {} 名员工，无法删除".format(emp_count))
        self.dept_repo.delete(dept)
        self.session.commit()
