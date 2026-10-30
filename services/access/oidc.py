"""Signature, issuer, audience and expiry are mandatory; no bypass."""
from typing import Annotated
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
