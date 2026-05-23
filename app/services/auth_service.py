from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def authenticate(self, username: str, password: str) -> tuple[User, str]:
        user = self.user_repo.get_by_username_with_roles(username)
        if not user:
            raise UnauthorizedException("用户名或密码错误")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("用户名或密码错误")
        if not user.is_active:
            raise UnauthorizedException("账号已被禁用")
        token = create_access_token(
            subject=str(user.id),
            extra={"username": user.username, "user_id": user.id},
        )
        return user, token

    def register(self, user_data: UserCreate) -> User:
        if self.user_repo.exists(username=user_data.username):
            raise ConflictException("用户名已存在")
        if user_data.email and self.user_repo.exists(email=user_data.email):
            raise ConflictException("邮箱已被注册")
        user = self.user_repo.create(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            is_active=True,
            is_superuser=False,
        )
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.user_repo.get_with_roles(user_id)
