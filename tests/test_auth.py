import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.models import User, Role


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_login_invalid_credentials(client: TestClient, db_session):
    role = Role(name="系统管理员", code="admin", is_system=True, permissions={})
    db_session.add(role)
    db_session.flush()

    user = User(
        username="testuser",
        hashed_password=hash_password("password123"),
        is_active=True,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        params={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_valid_credentials(client: TestClient, db_session):
    role = Role(name="系统管理员", code="admin", is_system=True, permissions={})
    db_session.add(role)
    db_session.flush()

    user = User(
        username="admin",
        hashed_password=hash_password("admin123"),
        is_active=True,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        params={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert data["data"]["username"] == "admin"


def test_me_unauthorized(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_ping(client: TestClient):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["message"] == "pong"
