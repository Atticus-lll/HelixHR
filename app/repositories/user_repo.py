from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self.session.scalar(select(User).where(User.username == username))

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_with_roles(self, user_id: int) -> User | None:
        return self.session.scalar(
            select(User).options(joinedload(User.roles)).where(User.id == user_id)
        )

    def get_by_username_with_roles(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).options(joinedload(User.roles)).where(User.username == username)
        )
