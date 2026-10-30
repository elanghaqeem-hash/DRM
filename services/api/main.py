"""DRM Bank: minimal Sprint 0 PoC API. NEVER handle real banking records."""
from typing import Annotated, Literal
import psycopg
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from services.api.settings import Settings, get_settings
from services.access.oidc import current_actor, require_roles
from services.audit.store import append_event, verify_chain

app = FastAPI(title="DRM Bank — Sprint 0 PoC", version="0.1.0",
              description="Non-production skeleton; Bank controls pending approval.")


class AuditIn(BaseModel):
    action: str = Field(min_length=1, max_length=80, pattern=r"^[A-Z0-9_]+$")
    object_ref: str = Field(min_length=1, max_length=200)
    before_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    after_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    result: Literal["SUCCESS", "DENIED", "FAILED"]


@app.get("/health/live", tags=["system"])
def live():
    return {"status": "alive", "phase": "SPRINT_0_POC"}


@app.get("/health/ready", tags=["system"])
def ready(settings: Annotated[Settings, Depends(get_settings)]):
    try:
        with psycopg.connect(settings.database_url, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        return {"status": "ready", "database": "available"}
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.post("/v1/audit/events", tags=["audit"], status_code=201)
def submit_audit_event(
    data: AuditIn, request: Request,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    role = require_roles(actor, {"audit_writer", "security_admin"})
    return append_event(
        settings.database_url, actor_sub=actor["sub"], actor_role=role,
        source_ip=request.client.host if request.client else None,
        device=None, action=data.action, object_ref=data.object_ref,
        before_hash=data.before_hash, after_hash=data.after_hash, result=data.result,
    )


@app.get("/v1/audit/verify", tags=["audit"])
def verify_audit(
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    require_roles(actor, {"auditor", "security_admin"})
    return verify_chain(settings.database_url)
