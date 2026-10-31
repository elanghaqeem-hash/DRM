import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from services.access.oidc import require_roles
from services.api.main import app
from services.api.settings import Settings


def test_health_live():
    assert TestClient(app).get("/health/live").json()["phase"] == "SPRINT_0_POC"


def test_private_endpoints_deny_anonymous():
    client = TestClient(app)
    assert client.get("/v1/audit/verify").status_code in (401, 403)
    assert client.post("/v1/audit/events", json={}).status_code in (401, 403)


def test_role_denied():
    with pytest.raises(HTTPException) as exc:
        require_roles({"realm_access": {"roles": ["record_creator"]}}, {"auditor"})
    assert exc.value.status_code == 403


def test_role_allowed():
    assert require_roles({"realm_access": {"roles": ["auditor"]}}, {"auditor"}) == "auditor"


def test_production_prohibited():
    values = dict(
        database_url="postgresql://example@localhost/db",
        oidc_issuer="http://example.local", oidc_jwks_url="http://example.local/jwks",
        oidc_audience="drm-api", drm_env="production", audit_anchor_required=True,
    )
    with pytest.raises(ValueError, match="not production-ready"):
        Settings(**values)
