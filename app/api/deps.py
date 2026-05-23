from typing import Callable, TypeVar

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User
from app.repositories import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

F = TypeVar("F", bound=Callable)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先提供访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌缺少用户信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_repo = UserRepository(session)
    user = user_repo.get_with_roles(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被删除",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员",
        )
    return user


def _check_roles(*role_names: str) -> Callable[[User], User]:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        owned_roles = {role.name for role in (current_user.roles or [])}
        if not owned_roles.intersection(role_names):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前账号没有足够权限")
        return current_user
    return checker


def _check_superuser() -> Callable[[User], User]:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要超级管理员权限")
        return current_user
    return checker


# These are pre-built Depends() instances ready to use directly in route handlers.
# Usage: current_user: User = Depends(AdminUser)
AdminUser: Callable[[], User] = _check_roles("系统管理员")
HRUser: Callable[[], User] = _check_roles("系统管理员", "人事专员")
SuperUser: Callable[[], User] = _check_superuser()
CurrentUser: Callable[[], User] = get_current_user
