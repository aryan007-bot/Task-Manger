"""
Unit tests for task CRUD endpoints.
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
    client.post("/api/auth/register", json={
        "full_name": "Task Tester", "email": "tasks@example.com", "password": "Password1"
    })
    res = client.post("/api/auth/login", json={"email": "tasks@example.com", "password": "Password1"})
    token = res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def task_id(client, auth_headers):
    res = client.post("/api/tasks", json={"title": "My test task", "priority": "high"}, headers=auth_headers)
    return res.get_json()["data"]["id"]


def test_create_task(client, auth_headers):
    res = client.post("/api/tasks", json={"title": "New task", "priority": "medium"}, headers=auth_headers)
    assert res.status_code == 201
    assert res.get_json()["data"]["title"] == "New task"


def test_create_task_missing_title(client, auth_headers):
    res = client.post("/api/tasks", json={"priority": "low"}, headers=auth_headers)
    assert res.status_code == 400


def test_create_task_invalid_priority(client, auth_headers):
    res = client.post("/api/tasks", json={"title": "Bad", "priority": "critical"}, headers=auth_headers)
    assert res.status_code == 400


def test_list_tasks(client, auth_headers):
    res = client.get("/api/tasks", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.get_json()["data"], list)


def test_list_tasks_filter_status(client, auth_headers):
    res = client.get("/api/tasks?status=pending", headers=auth_headers)
    assert res.status_code == 200


def test_get_task(client, auth_headers, task_id):
    res = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == task_id


def test_get_task_not_found(client, auth_headers):
    res = client.get("/api/tasks/999999", headers=auth_headers)
    assert res.status_code == 404


def test_update_task(client, auth_headers, task_id):
    res = client.put(f"/api/tasks/{task_id}", json={"status": "completed"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "completed"


def test_update_task_invalid_status(client, auth_headers, task_id):
    res = client.put(f"/api/tasks/{task_id}", json={"status": "done"}, headers=auth_headers)
    assert res.status_code == 400


def test_delete_task(client, auth_headers, task_id):
    res = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200


def test_delete_task_not_found(client, auth_headers, task_id):
    res = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 404


def test_tasks_require_auth(client):
    res = client.get("/api/tasks")
    assert res.status_code == 401
