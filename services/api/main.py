"""DRM Bank: minimal Sprint 0 PoC API. NEVER handle real banking records."""
from typing import Annotated, Literal
from pathlib import Path
from urllib.parse import urlsplit
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from uuid import UUID
from fastapi import Header, Query
from services.workspace.store import actor_workspace, list_tasks, create_task, decide_task
import psycopg
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from services.api.settings import Settings, get_settings
from services.access.oidc import current_actor, require_roles
from services.audit.store import append_event, verify_chain
from services.records.isolation import retention_preview, apply_legal_hold, release_legal_hold

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
    if not settings.legacy_audit_api_enabled:
        raise HTTPException(status_code=410, detail="Legacy global audit API retired")
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
    if not settings.legacy_audit_api_enabled:
        raise HTTPException(status_code=410, detail="Legacy global audit API retired")
    require_roles(actor, {"auditor", "security_admin"})
    return verify_chain(settings.database_url)


# EDARMS WP1: generic PoC approval inbox. Does not approve any records/destruction.


class TaskCreateIn(BaseModel):
    tenant_id: UUID
    title: str = Field(min_length=1, max_length=180)
    assigned_to: str = Field(min_length=1, max_length=255)


class TaskDecisionIn(BaseModel):
    tenant_id: UUID
    decision: Literal["APPROVED", "REJECTED"]
    expected_version: int = Field(ge=1)
    reason: str | None = Field(default=None, max_length=1000)


@app.get("/v1/workspace/me", tags=["workspace"])
def workspace_me(
    tenant_id: UUID,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return actor_workspace(settings.database_url, tenant_id, actor["sub"])


@app.get("/v1/workspace/tasks", tags=["workspace"])
def workspace_tasks(
    tenant_id: UUID,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
    status_filter: Literal["OPEN", "APPROVED", "REJECTED"] | None = None,
    limit: int = Query(default=25, ge=1, le=50),
):
    return list_tasks(settings.database_url, tenant_id, actor["sub"], status_filter, limit)


@app.post("/v1/workspace/tasks", tags=["workspace"], status_code=201)
def workspace_create_task(
    data: TaskCreateIn,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str, Header(min_length=8, max_length=128)],
):
    return create_task(settings.database_url, data.tenant_id, actor["sub"],
                       data.title, data.assigned_to, idempotency_key)


@app.post("/v1/workspace/tasks/{task_id}/decision", tags=["workspace"])
def workspace_decide_task(
    task_id: UUID,
    data: TaskDecisionIn,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return decide_task(settings.database_url, data.tenant_id, task_id, actor["sub"],
                       data.decision, data.expected_version, data.reason)


# Static PoC shell contains no secrets or synthetic bank records.
# Authenticated actions still occur exclusively through the API above.
WEB_ROOT = Path(__file__).resolve().parents[2] / "apps" / "web"
app.mount("/static", StaticFiles(directory=WEB_ROOT), name="edarms-static")


@app.get("/app", include_in_schema=False)
def poc_web_app():
    return FileResponse(WEB_ROOT / "index.html", media_type="text/html")


@app.get("/v1/public/oidc-config", tags=["system"])
def public_oidc_config(settings: Annotated[Settings, Depends(get_settings)]):
    return {"issuer": settings.oidc_issuer.rstrip("/"),
            "client_id": settings.oidc_web_client_id}


@app.middleware("http")
async def poc_web_security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/app" or request.url.path.startswith("/static/"):
        # Only own assets/scripts; Keycloak origin is allowed for OIDC token exchange.
        try:
            issuer_origin = urlsplit(get_settings().oidc_issuer)
            connect_origin = f"{issuer_origin.scheme}://{issuer_origin.netloc}"
        except Exception:
            connect_origin = "'none'"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
            "script-src 'self'; style-src 'self'; img-src 'self' data:; "
            f"connect-src 'self' {connect_origin}; "
            "form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
    return response


# WP2: tenant-gated read-only retention checks and human legal holds.
# These APIs never execute a disposition or certify a Bank JRA.
class HoldApplyIn(BaseModel):
    tenant_id: UUID
    case_ref: str = Field(min_length=2, max_length=200)
    legal_basis: str = Field(min_length=2, max_length=500)
    reason: str = Field(min_length=2, max_length=1000)


class HoldReleaseIn(BaseModel):
    tenant_id: UUID
    reason: str = Field(min_length=2, max_length=1000)


@app.get("/v1/archives/{record_id}/retention-preview", tags=["records"])
def preview_record_retention(
    record_id: UUID, tenant_id: UUID,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return retention_preview(settings.database_url, tenant_id, record_id, actor["sub"])


@app.post("/v1/archives/{record_id}/holds", tags=["legal"], status_code=201)
def create_record_hold(
    record_id: UUID, data: HoldApplyIn,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return apply_legal_hold(
        settings.database_url, data.tenant_id, record_id, actor["sub"],
        data.case_ref, data.legal_basis, data.reason,
    )


@app.post("/v1/legal-holds/{hold_id}/release", tags=["legal"])
def approve_hold_release(
    hold_id: UUID, data: HoldReleaseIn,
    actor: Annotated[dict, Depends(current_actor)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return release_legal_hold(
        settings.database_url, data.tenant_id, hold_id, actor["sub"], data.reason,
    )
