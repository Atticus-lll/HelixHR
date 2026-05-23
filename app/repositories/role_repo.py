from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model = Role

    def get_by_name(self, name: str) -> Role | None:
        return self.session.scalar(select(Role).where(Role.name == name))

    def get_by_code(self, code: str) -> Role | None:
        return self.session.scalar(select(Role).where(Role.code == code))
