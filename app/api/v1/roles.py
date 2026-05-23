from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import AdminUser, get_db
from app.core.exceptions import api_response
from app.core.pagination import PaginationParams
from app.models import User
from app.schemas import RoleCreate, RoleUpdate
from app.services.role_service import RoleService

router = APIRouter(prefix='/roles', tags=['角色管理'])


def _role_to_response(role) -> dict:
    return {
        'id': role.id,
        'name': role.name,
        'code': role.code,
        'description': role.description,
        'permissions': role.permissions or {},
        'is_system': role.is_system,
        'created_at': str(role.created_at),
    }


@router.post('/', status_code=status.HTTP_201_CREATED, summary='创建角色', responses={201: {"description": "创建成功"}, 403: {"description": "权限不足"}, 422: {"description": "参数校验失败"}})
async def create_role(
    role_data: RoleCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = RoleService(session)
    role = svc.create_role(role_data)
    return api_response(data=_role_to_response(role), message='角色创建成功', code=201)


@router.get('/', summary='获取角色列表（分页）', responses={200: {"description": "查询成功，返回角色列表"}, 403: {"description": "权限不足"}, 422: {"description": "参数校验失败"}})
async def list_roles(
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = RoleService(session)
    pagination = PaginationParams(page=page, page_size=page_size)
    result = svc.list_roles(pagination)
    items = [_role_to_response(r) for r in result.items]
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


@router.put('/{role_id}', summary='更新角色', responses={200: {"description": "更新成功"}, 403: {"description": "权限不足"}, 404: {"description": "角色不存在"}, 422: {"description": "参数校验失败"}})
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = RoleService(session)
    role = svc.update_role(role_id, role_data)
    return api_response(data=_role_to_response(role), message='角色更新成功')


@router.delete('/{role_id}', summary='删除角色', responses={200: {"description": "删除成功"}, 403: {"description": "权限不足"}, 404: {"description": "角色不存在"}})
async def delete_role(
    role_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(AdminUser),
):
    svc = RoleService(session)
    svc.delete_role(role_id)
    return api_response(data={'id': role_id}, message='角色删除成功')
