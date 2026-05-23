from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import AdminUser, CurrentUser, get_db
from app.core.exceptions import api_response
from app.core.pagination import PaginationParams
from app.models import User
from app.schemas import DeptCreate, DeptUpdate
from app.services.department_service import DepartmentService

router = APIRouter(prefix='/departments', tags=['部门管理'])


def _dept_to_response(dept, employee_count: int = 0) -> dict:
    return {
        'id': dept.id,
        'name': dept.name,
        'code': dept.code,
        'parent_id': dept.parent_id,
        'manager_id': dept.manager_id,
        'description': dept.description,
        'employee_count': employee_count,
        'created_at': str(dept.created_at),
        'updated_at': str(dept.updated_at) if dept.updated_at else None,
    }


@router.post('/', status_code=status.HTTP_201_CREATED, summary='创建部门', responses={201: {"description": "创建成功"}, 403: {"description": "权限不足"}, 422: {"description": "参数校验失败"}})
async def create_department(
    dept_data: DeptCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = DepartmentService(session)
    dept = svc.create_department(dept_data)
    return api_response(data=_dept_to_response(dept), message='部门创建成功', code=201)


@router.get('/', summary='获取部门列表（分页）', responses={200: {"description": "查询成功，返回部门列表"}, 401: {"description": "未登录"}, 422: {"description": "参数校验失败"}})
async def list_departments(
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    session: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    svc = DepartmentService(session)
    pagination = PaginationParams(page=page, page_size=page_size)
    result = svc.list_departments(pagination)
    items = [_dept_to_response(d) for d in result.items]
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


@router.get('/{department_id}', summary='获取部门详情', responses={200: {"description": "查询成功，返回部门详情"}, 404: {"description": "部门不存在"}})
async def get_department(
    department_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    svc = DepartmentService(session)
    dept = svc.get_department(department_id)
    return api_response(data=_dept_to_response(dept))


@router.put('/{department_id}', summary='更新部门信息', responses={200: {"description": "更新成功"}, 403: {"description": "权限不足"}, 404: {"description": "部门不存在"}, 422: {"description": "参数校验失败"}})
async def update_department(
    department_id: int,
    dept_data: DeptUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = DepartmentService(session)
    dept = svc.update_department(department_id, dept_data)
    return api_response(data=_dept_to_response(dept), message='部门更新成功')


@router.delete('/{department_id}', summary='删除部门', responses={200: {"description": "删除成功"}, 403: {"description": "权限不足"}, 404: {"description": "部门不存在"}})
async def delete_department(
    department_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = DepartmentService(session)
    svc.delete_department(department_id)
    return api_response(data={'id': department_id}, message='部门删除成功')
