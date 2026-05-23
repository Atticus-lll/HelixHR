import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models import Role, User


def _create_admin(db: Session) -> User:
    role = Role(name="系统管理员", code="admin", is_system=True, permissions={"*": True})
    db.add(role)
    db.flush()
    user = User(username="rag_admin", hashed_password=hash_password("admin123"), is_active=True)
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_rag_stats(client: TestClient, db_session: Session):
    admin = _create_admin(db_session)
    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.get("/api/v1/rag/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "collection_name" in data["data"]


def test_rag_list_documents(client: TestClient, db_session: Session):
    admin = _create_admin(db_session)
    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.get("/api/v1/rag/documents", headers=headers)
    assert response.status_code == 200


def test_rag_ingest_text(client: TestClient, db_session: Session):
    admin = _create_admin(db_session)
    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    response = client.post(
        "/api/v1/rag/documents/text",
        params={
            "title": "员工手册",
            "content": "本手册介绍公司规章制度。员工上班时间为早上九点，下班时间为下午六点。",
            "source": "HR部门",
            "tags": "规章制度,员工手册",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["chunks_count"] > 0
    assert data["data"]["status"] == "indexed"


def test_rag_query_after_ingest(client: TestClient, db_session: Session):
    admin = _create_admin(db_session)
    token = create_access_token(subject=str(admin.id), extra={"user_id": admin.id, "username": admin.username})
    headers = {"Authorization": "Bearer {}".format(token)}

    client.post(
        "/api/v1/rag/documents/text",
        params={
            "title": "考勤制度",
            "content": "公司实行弹性工作制，加班需提前申请并获得主管批准。",
        },
        headers=headers,
    )

    response = client.post(
        "/api/v1/rag/query",
        json={"query": "加班政策是什么？", "top_k": 3},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total_results"] >= 0
