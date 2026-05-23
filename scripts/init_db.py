#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import Base, Dept, Role, User
from app.models import sys_user_role


def init_database():
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

    session = SessionLocal()
    try:
        existing_admin = session.query(User).filter(User.username == settings.admin.username).first()
        if existing_admin:
            print("管理员账号 {} 已存在，跳过创建。".format(settings.admin.username))
            return

        admin_role = session.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            admin_role = Role(
                name=settings.admin.role_name,
                code="admin",
                description="系统管理员，拥有所有权限",
                permissions={"*": True},
                is_system=True,
            )
            session.add(admin_role)
            session.flush()
            print("创建角色: {}".format(admin_role.name))

        hr_role = session.query(Role).filter(Role.code == "hr").first()
        if not hr_role:
            hr_role = Role(
                name="人事专员",
                code="hr",
                description="人事专员，负责员工和薪资管理",
                permissions={
                    "employee:read": True,
                    "employee:write": True,
                    "salary:read": True,
                    "salary:write": True,
                    "department:read": True,
                },
                is_system=True,
            )
            session.add(hr_role)
            session.flush()
            print("创建角色: 人事专员")

        user_role = session.query(Role).filter(Role.code == "user").first()
        if not user_role:
            user_role = Role(
                name="普通员工",
                code="user",
                description="普通员工，仅可查看部分信息",
                permissions={
                    "employee:read": True,
                    "department:read": True,
                },
                is_system=True,
            )
            session.add(user_role)
            session.flush()
            print("创建角色: 普通员工")

        admin_user = User(
            username=settings.admin.username,
            hashed_password=hash_password(settings.admin.password),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True,
        )
        session.add(admin_user)
        session.flush()
        session.execute(
            sys_user_role.insert().values(user_id=admin_user.id, role_id=admin_role.id)
        )
        print("创建管理员账号: {} / {}".format(admin_user.username, settings.admin.password))

        dept_tech = Dept(name="技术部", code="TECH", description="负责技术研发")
        dept_hr = Dept(name="人力资源部", code="HR", description="负责人员管理")
        dept_sales = Dept(name="销售部", code="SALES", description="负责产品销售")
        dept_finance = Dept(name="财务部", code="FIN", description="负责财务管理")
        session.add_all([dept_tech, dept_hr, dept_sales, dept_finance])
        session.flush()
        print("创建默认部门: 技术部, 人力资源部, 销售部, 财务部")

        session.commit()
        print("数据库初始化完成！")

    except Exception as e:
        session.rollback()
        print("初始化失败: {}".format(e))
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
