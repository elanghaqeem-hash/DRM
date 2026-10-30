"""All archive and legal APIs deny anonymous and expose no unscoped controls."""
from fastapi.testclient import TestClient

from services.api.main import app


def test_archive_api_requires_oidc_token():
    client = TestClient(app)
    rid = "11111111-1111-4111-8111-111111111111"
    tid = "22222222-2222-4222-8222-222222222222"
    preview = client.get(
        f"/v1/archives/{rid}/retention-preview", params={"tenant_id": tid}
    )
    assert preview.status_code in (401, 403)
    hold = client.post(
        f"/v1/archives/{rid}/holds",
        json={"tenant_id": tid, "case_ref": "SYNTHETIC",
              "legal_basis": "SYNTHETIC", "reason": "SYNTHETIC"},
    )
    assert hold.status_code in (401, 403)
    release = client.post(
        f"/v1/legal-holds/{rid}/release",
        json={"tenant_id": tid, "reason": "SYNTHETIC"},
    )
    assert release.status_code in (401, 403)


def test_anonymous_legacy_audit_api_cannot_return_global_ledger():
    response = TestClient(app).get("/v1/audit/verify")
    assert response.status_code in (401, 403)
