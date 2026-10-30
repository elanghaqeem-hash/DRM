"""Settings fail closed outside the local proof of concept."""
from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = Field(min_length=12)
    oidc_issuer: str = Field(min_length=5)
    oidc_jwks_url: str = Field(min_length=5)
    oidc_audience: str = Field(min_length=1)
    oidc_web_client_id: str = Field(default="drm-web", min_length=3)
    oidc_required_acr: str | None = None  # Bank-signed IdP assurance profile TBD-BANK
    oidc_enforce: bool = True
    drm_env: str = "poc"
    audit_anchor_required: bool = False
    legacy_audit_api_enabled: bool = False  # global ledger is not tenant-isolated

    @model_validator(mode="after")
    def validate_settings(self):
        if self.drm_env == "production":
            raise ValueError("Sprint 0 is not production-ready: startup blocked")
        if self.drm_env != "poc" and not self.oidc_required_acr:
            raise ValueError("Bank-approved OIDC ACR required outside PoC")
        if self.drm_env != "poc" and not self.oidc_enforce:
            raise ValueError("OIDC cannot be disabled outside PoC")
        if self.drm_env != "poc" and not self.audit_anchor_required:
            raise ValueError("External WORM anchor is required outside PoC")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
