"""
Unit tests for authentication endpoints.
Run with: pytest task-manager/tests/ -v
"""
import pytest
from app import create_app
from app.extensions import db
from app.config.config import TestingConfig


@pytest.fixture(scope="module")
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def auth_headers(client):
    """Register and log in a test user, return JWT headers."""
    client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "Password1",
    })
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "Password1"})
    token = res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_success(client):
    res = client.post("/api/auth/register", json={
        "full_name": "New User",
        "email": "new@example.com",
        "password": "Password1",
    })
    assert res.status_code == 201
    assert res.get_json()["success"] is True


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "full_name": "Dup User", "email": "dup@example.com", "password": "Password1"
    })
    res = client.post("/api/auth/register", json={
        "full_name": "Dup User 2", "email": "dup@example.com", "password": "Password1"
    })
    assert res.status_code == 400


def test_register_missing_fields(client):
    res = client.post("/api/auth/register", json={"email": "x@x.com"})
    assert res.status_code == 400


def test_register_weak_password(client):
    res = client.post("/api/auth/register", json={
        "full_name": "Weak", "email": "weak@example.com", "password": "short"
    })
    assert res.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={
        "full_name": "Login Test", "email": "login@example.com", "password": "Password1"
    })
    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "Password1"})
    assert res.status_code == 200
    assert "access_token" in res.get_json()["data"]


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "WrongPass1"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "Password1"})
    assert res.status_code == 401


def test_me_authenticated(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert "email" in res.get_json()["data"]


def test_me_unauthenticated(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_logout(client, auth_headers):
    res = client.post("/api/auth/logout", headers=auth_headers)
    assert res.status_code == 200
