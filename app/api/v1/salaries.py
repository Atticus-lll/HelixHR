from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import HRUser, get_db
from app.core.exceptions import api_response
from app.core.pagination import PaginationParams
from app.models import User
from app.schemas import SalaryCreate, SalaryUpdate
from app.services.salary_service import SalaryService

router = APIRouter(prefix='/salaries', tags=['薪资管理'])


def _salary_to_response(sal) -> dict:
    return {
        'id': sal.id,
        'employee_id': sal.employee_id,
        'base_salary': str(sal.base_salary),
        'bonus': str(sal.bonus),
        'deductions': str(sal.deductions),
        'tax': str(sal.tax),
        'allowances': str(sal.allowances),
        'net_salary': str(sal.net_salary),
        'pay_month': str(sal.pay_month),
        'payment_date': str(sal.payment_date) if sal.payment_date else None,
        'payment_status': sal.payment_status,
        'created_at': str(sal.created_at),
        'updated_at': str(sal.updated_at) if sal.updated_at else None,
    }


@router.post('/', status_code=status.HTTP_201_CREATED, summary='录入薪资记录', responses={201: {"description": "创建成功"}, 403: {"description": "权限不足"}, 422: {"description": "参数校验失败"}})
async def create_salary(
    salary_data: SalaryCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = SalaryService(session)
    sal = svc.create_salary(salary_data, current_user.id)
    return api_response(data=_salary_to_response(sal), message='薪资记录创建成功', code=201)


@router.get('/', summary='获取薪资记录列表（分页）', responses={200: {"description": "查询成功，返回薪资列表"}, 403: {"description": "权限不足"}, 422: {"description": "参数校验失败"}})
async def list_salaries(
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    employee_id: int | None = Query(None, description='员工ID'),
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = SalaryService(session)
    pagination = PaginationParams(page=page, page_size=page_size)
    result = svc.list_salaries(pagination, employee_id=employee_id)
    items = [_salary_to_response(s) for s in result.items]
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


@router.get('/{salary_id}', summary='获取薪资详情', responses={200: {"description": "查询成功，返回薪资详情"}, 404: {"description": "记录不存在"}})
async def get_salary(
    salary_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = SalaryService(session)
    sal = svc.get_salary(salary_id)
    return api_response(data=_salary_to_response(sal))


@router.put('/{salary_id}', summary='更新薪资记录', responses={200: {"description": "更新成功"}, 403: {"description": "权限不足"}, 404: {"description": "记录不存在"}, 422: {"description": "参数校验失败"}})
async def update_salary(
    salary_id: int,
    salary_data: SalaryUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = SalaryService(session)
    sal = svc.update_salary(salary_id, salary_data)
    return api_response(data=_salary_to_response(sal), message='薪资记录更新成功')


@router.get('/employee/{employee_id}', summary='获取员工薪资历史', responses={200: {"description": "查询成功，返回薪资历史"}, 404: {"description": "员工不存在"}, 422: {"description": "参数校验失败"}})
async def get_employee_salary_history(
    employee_id: int,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    session: Session = Depends(get_db),
    current_user: User = Depends(HRUser),
):
    svc = SalaryService(session)
    pagination = PaginationParams(page=page, page_size=page_size)
    result = svc.get_employee_salary_history(employee_id, pagination)
    items = [_salary_to_response(s) for s in result.items]
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
