from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import AdminUser, CurrentUser, get_db
from app.core.exceptions import api_response
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix='/auth', tags=['认证授权'])


@router.post('/login', summary='用户登录', responses={200: {"description": "登录成功，返回访问令牌"}, 401: {"description": "用户名或密码错误"}, 422: {"description": "参数校验失败"}})
async def login(
    username: str = Query(..., description='用户名'),
    password: str = Query(..., description='密码'),
    session: Session = Depends(get_db),
):
    auth_svc = AuthService(session)
    user, token = auth_svc.authenticate(username, password)
    return api_response(
        data={
            'access_token': token,
            'token_type': 'bearer',
            'user_id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'roles': [r.name for r in user.roles],
        },
        message='登录成功',
        code=200,
    )


@router.post('/register', status_code=status.HTTP_201_CREATED, summary='注册新用户', responses={201: {"description": "注册成功，返回用户信息"}, 403: {"description": "权限不足，仅管理员可注册"}, 422: {"description": "参数校验失败"}})
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_db),
    _: User = Depends(AdminUser),
):
    auth_svc = AuthService(session)
    user = auth_svc.register(user_data)
    return api_response(
        data=UserResponse.model_validate(user).model_dump(),
        message='用户注册成功',
        code=201,
    )


@router.get('/me', summary='获取当前用户信息', responses={200: {"description": "获取成功，返回当前用户信息"}, 401: {"description": "未登录或令牌无效"}})
async def get_current_user_info(
    current_user: User = Depends(CurrentUser),
):
    return api_response(
        data={
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'is_active': current_user.is_active,
            'is_superuser': current_user.is_superuser,
            'roles': [r.name for r in current_user.roles],
            'created_at': str(current_user.created_at),
        },
        message='获取用户信息成功',
        code=200,
    )
