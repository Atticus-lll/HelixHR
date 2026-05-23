from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.core.pagination import PageResult, PaginationParams
from app.models import Role
from app.repositories import RoleRepository
from app.schemas import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, session: Session):
        self.session = session
        self.role_repo = RoleRepository(session)

    def create_role(self, role_data: RoleCreate) -> Role:
        if self.role_repo.exists(name=role_data.name):
            raise ConflictException("角色名称已存在")
        if self.role_repo.get_by_code(role_data.code):
            raise ConflictException("角色编码已存在")
        role = self.role_repo.create(**{k: v for k, v in role_data.model_dump().items() if v is not None})
        self.session.commit()
        self.session.refresh(role)
        return role

    def get_role(self, role_id: int) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundException("角色不存在")
        return role

    def list_roles(self, pagination: PaginationParams) -> PageResult[Role]:
        roles = self.role_repo.get_multi(
            offset=pagination.offset, limit=pagination.limit,
            order_by="created_at", order_desc=True,
        )
        total = self.role_repo.count()
        return PageResult(items=roles, total=total, page=pagination.page, page_size=pagination.page_size)

    def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundException("角色不存在")
        if role.is_system:
            raise ForbiddenException("系统内置角色不可修改")
        payload = role_data.model_dump(exclude_unset=True, exclude_none=True)
        role = self.role_repo.update(role, **payload)
        self.session.commit()
        self.session.refresh(role)
        return role

    def delete_role(self, role_id: int) -> None:
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundException("角色不存在")
        if role.is_system:
            raise ForbiddenException("系统内置角色不可删除")
        self.role_repo.delete(role)
        self.session.commit()
