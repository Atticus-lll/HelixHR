from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Dept
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Dept]):
    model = Dept

    def get_by_code(self, code: str) -> Dept | None:
        return self.session.scalar(select(Dept).where(Dept.code == code))

    def get_by_name(self, name: str) -> Dept | None:
        return self.session.scalar(select(Dept).where(Dept.name == name))

    def get_children(self, parent_id: int) -> list[Dept]:
        return list(self.session.scalars(
            select(Dept).where(Dept.parent_id == parent_id)
        ).all())
