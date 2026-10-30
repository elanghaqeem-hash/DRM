"""Smoke tests for the actual EDARMS PoC UI route (no IdP session required)."""
from fastapi.testclient import TestClient
from services.api.main import app


def test_workspace_shell_is_served_with_security_headers():
    response = TestClient(app).get("/app")
    assert response.status_code == 200
    assert "My Tasks & Approval Inbox" in response.text
    assert "ROADMAP" in response.text
    assert "Content-Security-Policy" in response.headers
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store"


def test_web_assets_are_real_files():
    client = TestClient(app)
    script = client.get("/static/edarms.js")
    style = client.get("/static/edarms.css")
    assert script.status_code == 200
    assert "startLogin" in script.text
    assert style.status_code == 200
    assert ".sidebar" in style.text


def test_workspace_api_requires_token():
    response = TestClient(app).get(
        "/v1/workspace/tasks", params={"tenant_id": "11111111-1111-4111-8111-111111111111"}
    )
    assert response.status_code in (401, 403)
