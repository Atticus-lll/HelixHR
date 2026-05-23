from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import AdminUser, CurrentUser, HRUser, get_db
from app.core.exceptions import api_response
from app.core.pagination import PaginationParams
from app.models import User
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(prefix='/employees', tags=['员工管理'])


def _emp_to_response(emp) -> dict:
    return {
        'id': emp.id,
        'employee_number': emp.employee_number,
        'name': emp.name,
        'email': emp.email,
        'phone': emp.phone,
        'id_card': emp.id_card,
        'gender': emp.gender,
        'birth_date': str(emp.birth_date) if emp.birth_date else None,
        'hire_date': str(emp.hire_date) if emp.hire_date else None,
        'department_id': emp.department_id,
        'department_name': emp.department.name if emp.department else None,
        'position': emp.position,
        'employment_status': emp.employment_status,
        'address': emp.address,
        'emergency_contact': emp.emergency_contact,
        'emergency_phone': emp.emergency_phone,
        'created_at': str(emp.created_at),
        'updated_at': str(emp.updated_at) if emp.updated_at else None,
    }


@router.post('/', status_code=status.HTTP_201_CREATED, summary='创建员工', responses={201: {"description": "创建成功"}, 403: {"description": "权限不足"}, 422: {"description": "参数校验失败"}})
async def create_employee(
    emp_data: EmployeeCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = EmployeeService(session)
    emp = svc.create_employee(emp_data, current_user.id)
    return api_response(data=_emp_to_response(emp), message='员工创建成功', code=201)


@router.get('/', summary='获取员工列表（分页）', responses={200: {"description": "查询成功，返回员工列表"}, 401: {"description": "未登录"}, 422: {"description": "参数校验失败"}})
async def list_employees(
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    department_id: int | None = Query(None, description='部门ID'),
    employment_status: str | None = Query(None, description='在职状态'),
    session: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    svc = EmployeeService(session)
    pagination = PaginationParams(page=page, page_size=page_size)
    result = svc.list_employees(
        pagination=pagination,
        department_id=department_id,
        employment_status=employment_status,
    )
    items = [_emp_to_response(emp) for emp in result.items]
    return api_response(
        data={
            'items': items,
            'total': result.total,
            'page': result.page,
            'page_size': result.page_size,
            'total_pages': result.total_pages,
        },
        message='查询成功',
    )


@router.get('/{employee_id}', summary='获取员工详情', responses={200: {"description": "查询成功，返回员工详情"}, 404: {"description": "员工不存在"}})
async def get_employee(
    employee_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    svc = EmployeeService(session)
    emp = svc.get_employee(employee_id)
    return api_response(data=_emp_to_response(emp))


@router.put('/{employee_id}', summary='更新员工信息', responses={200: {"description": "更新成功"}, 403: {"description": "权限不足"}, 404: {"description": "员工不存在"}, 422: {"description": "参数校验失败"}})
async def update_employee(
    employee_id: int,
    emp_data: EmployeeUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = EmployeeService(session)
    emp = svc.update_employee(employee_id, emp_data)
    return api_response(data=_emp_to_response(emp), message='员工更新成功')


@router.delete('/{employee_id}', summary='删除员工', responses={200: {"description": "删除成功"}, 403: {"description": "权限不足"}, 404: {"description": "员工不存在"}})
async def delete_employee(
    employee_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = EmployeeService(session)
    svc.delete_employee(employee_id)
    return api_response(data={'id': employee_id}, message='员工删除成功')
