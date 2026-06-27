import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models import Dept, Employee, Role, User


def _create_admin_user(db: Session) -> User:
    role = Role(name="系统管理员", code="admin", is_system=True, permissions={})
    db.add(role)
    db.flush()
    user = User(username="admin", hashed_password=hash_password("admin123"), is_active=True)
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_employee(client: TestClient, db_session: Session):
    admin = _create_admin_user(db_session)
    dept = Dept(name="技术部", code="TECH")
    db_session.add(dept)
    db_session.commit()

    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.post(
        "/api/v1/employees/",
        json={
            "employee_number": "E001",
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "department_id": dept.id,
            "position": "工程师",
            "hire_date": "2024-01-15",
            "employment_status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "张三"
    assert data["data"]["employee_number"] == "E001"


def test_list_employees(client: TestClient, db_session: Session):
    admin = _create_admin_user(db_session)
    dept = Dept(name="销售部", code="SALES")
    db_session.add(dept)
    db_session.flush()

    for i in range(3):
        emp = Employee(
            employee_number="E{:03d}".format(i),
            name="员工{}".format(i),
            department_id=dept.id,
            position="员工",
            employment_status="active",
            created_by=admin.id,
        )
        db_session.add(emp)
    db_session.commit()

    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.get("/api/v1/employees/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] == 3


def test_get_employee(client: TestClient, db_session: Session):
    admin = _create_admin_user(db_session)
    dept = Dept(name="财务部", code="FIN")
    db_session.add(dept)
    db_session.flush()

    emp = Employee(
        employee_number="E999",
        name="李四",
        department_id=dept.id,
        position="会计",
        employment_status="active",
        created_by=admin.id,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.get("/api/v1/employees/{}".format(emp.id), headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "李四"


def test_delete_employee(client: TestClient, db_session: Session):
    admin = _create_admin_user(db_session)
    dept = Dept(name="技术部", code="TECH")
    db_session.add(dept)
    db_session.flush()

    emp = Employee(
        employee_number="E200",
        name="赵六",
        department_id=dept.id,
        position="实习生",
        employment_status="active",
        created_by=admin.id,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    emp_id = emp.id

    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.delete("/api/v1/employees/{}".format(emp_id), headers=headers)
    assert response.status_code == 200
