"""Signed-token MFA assurance gating: synthetic unit evidence, not Bank IdP UAT."""
from time import time
import pytest
from fastapi import HTTPException
from services.access.oidc import require_recent_mfa
from services.api.settings import Settings


def settings(**overrides):
    params = {
        "database_url": "postgresql://synthetic@localhost/test",
        "oidc_issuer": "https://idp.example.test/realms/edarms",
        "oidc_jwks_url": "https://idp.example.test/certs",
        "oidc_audience": "drm-api",
        "oidc_mfa_required": True,
        "oidc_allowed_acr": "urn:bank:assurance:mfa",
        "oidc_allowed_amr": "mfa,hwk",
        "drm_env": "poc",
    }
    params.update(overrides)
    return Settings(**params)


def test_recent_mfa_accepts_configured_signed_claims():
    conf = settings()
    require_recent_mfa(
        {"acr": "urn:bank:assurance:mfa", "auth_time": int(time())}, conf
    )
    require_recent_mfa({"amr": ["pwd", "hwk"], "auth_time": int(time())}, conf)


@pytest.mark.parametrize("claims", [
    {},
    {"amr": ["pwd"], "auth_time": int(time())},
    {"acr": "urn:bank:assurance:password", "auth_time": int(time())},
    {"amr": ["mfa"], "auth_time": int(time()) - 3600},
    {"amr": ["mfa"], "auth_time": True},
    {"amr": ["mfa"], "auth_time": int(time()) + 3600},
])
def test_missing_stale_or_password_only_mfa_denied(claims):
    with pytest.raises(HTTPException) as exc:
        require_recent_mfa(claims, settings())
    assert exc.value.status_code == 403


def test_mfa_mandatory_outside_poc():
    with pytest.raises(ValueError, match="MFA enforcement"):
        settings(
            drm_env="staging", oidc_mfa_required=False,
            audit_anchor_required=True,
        )
