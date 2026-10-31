"""Signature, issuer, audience and expiry are mandatory; no bypass."""
from typing import Annotated
from time import time
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.api.settings import Settings, get_settings

bearer = HTTPBearer(auto_error=True)


def validate_access_token(token: str, settings: Settings) -> dict:
    if not settings.oidc_enforce:
        raise HTTPException(status_code=503, detail="OIDC bypass disabled")
    try:
        client = jwt.PyJWKClient(settings.oidc_jwks_url, cache_jwk_set=True, lifespan=300)
        key = client.get_signing_key_from_jwt(token).key
        return jwt.decode(
            token, key, algorithms=["RS256"], audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
            options={"require": ["sub", "exp", "iss", "aud", "iat"]},
        )
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid access token") from exc


def current_actor(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    return validate_access_token(credentials.credentials, settings)


def require_roles(actor: dict, allowed: set[str]) -> str:
    assigned = set(actor.get("realm_access", {}).get("roles", []))
    matched = allowed & assigned
    if not matched:
        raise HTTPException(status_code=403, detail="Insufficient role")
    return sorted(matched)[0]


def require_recent_mfa(actor: dict, settings: Settings) -> None:
    """Require a *signed* MFA assurance claim and recent authentication.

    Bank IAM must approve the accepted ACR/AMR values and verify IdP token
    mapping. A password-only claim never counts as MFA.
    """
    if not settings.oidc_mfa_required:
        return  # Disposable local PoC only; non-PoC settings reject this mode.
    acceptable_acr = {x.strip() for x in settings.oidc_allowed_acr.split(",") if x.strip()}
    acceptable_amr = {x.strip() for x in settings.oidc_allowed_amr.split(",") if x.strip()}
    acr = actor.get("acr")
    amr = actor.get("amr")
    assurance = (isinstance(acr, str) and acr in acceptable_acr) or (
        isinstance(amr, list) and bool(acceptable_amr.intersection(amr))
    )
    auth_time = actor.get("auth_time")
    now = time()
    if not assurance or type(auth_time) is not int or not (
        0 <= now - auth_time <= settings.oidc_max_auth_age_seconds
    ):
        raise HTTPException(status_code=403, detail="Recent Bank MFA required")
