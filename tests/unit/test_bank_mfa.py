from fastapi import HTTPException
import pytest
from services.access.oidc import require_bank_mfa


def test_bank_mfa_required_acr_matches_issued_claim():
    require_bank_mfa({"acr": "synthetic-bank-mfa"}, "synthetic-bank-mfa")


@pytest.mark.parametrize("claims", [{}, {"acr": "low"}, {"amr": ["otp"]}])
def test_bank_mfa_rejects_missing_or_wrong_assurance(claims):
    with pytest.raises(HTTPException) as exc:
        require_bank_mfa(claims, "synthetic-bank-mfa")
    assert exc.value.status_code == 403


def test_poc_without_bank_acr_does_not_claim_bank_mfa():
    require_bank_mfa({}, None)
