"""
Unit tests for the analytics endpoint.
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
        "full_name": "Analytics User", "email": "analytics@example.com", "password": "Password1"
    })
    res = client.post("/api/auth/login", json={"email": "analytics@example.com", "password": "Password1"})
    token = res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_analytics_unauthenticated(client):
    res = client.get("/api/analytics")
    assert res.status_code == 401


def test_analytics_empty(client, auth_headers):
    res = client.get("/api/analytics", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_tasks"] == 0
    assert data["completion_percentage"] == 0.0


def test_analytics_with_tasks(client, auth_headers):
    # Seed tasks
    tasks = [
        {"title": "A", "priority": "high",   "status": "completed"},
        {"title": "B", "priority": "medium",  "status": "pending"},
        {"title": "C", "priority": "low",     "status": "in_progress"},
        {"title": "D", "priority": "high",    "status": "pending"},
    ]
    for t in tasks:
        client.post("/api/tasks", json=t, headers=auth_headers)

    res = client.get("/api/analytics", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_tasks"] == 4
    assert data["completed_tasks"] == 1
    assert data["pending_tasks"] == 2
    assert data["in_progress_tasks"] == 1
    assert data["completion_percentage"] == 25.0


def test_analytics_priority_distribution(client, auth_headers):
    res = client.get("/api/analytics", headers=auth_headers)
    pd = res.get_json()["data"]["priority_distribution"]
    assert "high" in pd and "medium" in pd and "low" in pd


def test_analytics_trend_shape(client, auth_headers):
    res = client.get("/api/analytics", headers=auth_headers)
    trend = res.get_json()["data"]["task_trend"]
    assert "labels" in trend and "values" in trend
    assert len(trend["labels"]) == len(trend["values"])
