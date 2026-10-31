"""Tenant-scoped, transactional PoC review task store.

This generic inbox cannot approve legal holds, record declarations or destruction.
Only synthetic sandbox identities may be provisioned until Bank sign-off.
"""
from uuid import UUID
import psycopg
from psycopg.rows import dict_row
from fastapi import HTTPException
from services.workspace.policy import (
    CREATE_ROLES, DECIDE_ROLES, ReviewTask, WorkspacePolicyError,
    check_decision, require_scoped_role,
)


def _start_scope(conn: psycopg.Connection, tenant_id: UUID, actor_sub: str) -> set[str]:
    """Trust the verified OIDC subject; cross-check membership in database."""
    if not actor_sub or len(actor_sub) > 255:
        raise HTTPException(status_code=403, detail="Active tenant membership required")
    # DB owners/superusers can bypass RLS; no API operation may use one.
    db_role = conn.execute(
        "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user"
    ).fetchone()
    if db_role is None or db_role["rolsuper"] or db_role["rolbypassrls"]:
        raise HTTPException(status_code=503, detail="Unsafe database identity: RLS bypass")
    # LOCAL setting lasts only for this transaction and is used by FORCE RLS.
    conn.execute("SELECT set_config('edarms.tenant_id', %s, true)", (str(tenant_id),))
    rows = conn.execute(
        """SELECT role_code FROM edarms_membership
           WHERE tenant_id=%s AND actor_sub=%s AND enabled=true""",
        (tenant_id, actor_sub),
    ).fetchall()
    roles = {row["role_code"] for row in rows}
    if not roles:
        raise HTTPException(status_code=403, detail="Active tenant membership required")
    return roles


def _role(roles: set[str], allow: frozenset[str]) -> None:
    try:
        require_scoped_role(roles, allow)
    except WorkspacePolicyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


def actor_workspace(database_url: str, tenant_id: UUID, actor_sub: str) -> dict:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor_sub)
            return {
                "tenant_id": str(tenant_id), "subject": actor_sub,
                "roles": sorted(roles),
                "abilities": {
                    "task_create": bool(CREATE_ROLES & roles),
                    "task_decide": bool(DECIDE_ROLES & roles),
                },
                "released_menu_ids": ["A2"],
                "release_scope": "POC_GENERIC_TASK_ONLY",
            }


def list_tasks(
    database_url: str, tenant_id: UUID, actor_sub: str,
    status: str | None = None, limit: int = 25,
) -> dict:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            _start_scope(conn, tenant_id, actor_sub)
            rows = conn.execute(
                """SELECT id,title,assigned_to,created_by,status,version,created_at,
                          decided_by,decided_at,decision_reason
                   FROM edarms_review_task
                   WHERE tenant_id=%s AND (assigned_to=%s OR created_by=%s)
                     AND (%s::text IS NULL OR status=%s)
                   ORDER BY created_at DESC,id DESC LIMIT %s""",
                (tenant_id, actor_sub, actor_sub, status, status, limit),
            ).fetchall()
            return {"items": [dict(row) for row in rows], "limit": limit}


def create_task(
    database_url: str, tenant_id: UUID, actor_sub: str,
    title: str, assigned_to: str, idempotency_key: str,
) -> dict:
    if not title.strip() or title != title.strip():
        raise HTTPException(status_code=422, detail="Valid title required")
    if assigned_to == actor_sub:
        raise HTTPException(status_code=422, detail="Checker must be independent")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor_sub)
            _role(roles, CREATE_ROLES)
            checker = conn.execute(
                """SELECT 1 FROM edarms_membership
                   WHERE tenant_id=%s AND actor_sub=%s AND enabled=true
                         AND role_code IN ('approver','records_manager') LIMIT 1""",
                (tenant_id, assigned_to),
            ).fetchone()
            if checker is None:
                raise HTTPException(status_code=422, detail="Assigned checker not provisioned")
            created = conn.execute(
                """INSERT INTO edarms_review_task
                   (tenant_id,title,created_by,assigned_to,idempotency_key)
                   VALUES (%s,%s,%s,%s,%s)
                   ON CONFLICT (tenant_id,created_by,idempotency_key) DO NOTHING
                   RETURNING id,title,created_by,assigned_to,status,version""",
                (tenant_id, title, actor_sub, assigned_to, idempotency_key),
            ).fetchone()
            if created is not None:
                conn.execute(
                    """INSERT INTO edarms_task_event
                       (tenant_id,task_id,actor_sub,action)
                       VALUES (%s,%s,%s,'CREATED')""",
                    (tenant_id, created["id"], actor_sub),
                )
                return {**dict(created), "idempotent_replay": False}
            existing = conn.execute(
                """SELECT id,title,created_by,assigned_to,status,version
                   FROM edarms_review_task WHERE tenant_id=%s AND created_by=%s
                   AND idempotency_key=%s""",
                (tenant_id, actor_sub, idempotency_key),
            ).fetchone()
            if existing is None:
                raise HTTPException(status_code=409, detail="Idempotency collision")
            if existing["title"] != title or existing["assigned_to"] != assigned_to:
                raise HTTPException(status_code=409, detail="Idempotency key reused with new payload")
            return {**dict(existing), "idempotent_replay": True}


def decide_task(
    database_url: str, tenant_id: UUID, task_id: UUID, actor_sub: str,
    decision: str, expected_version: int, reason: str | None,
) -> dict:
    if decision not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=422, detail="Unsupported decision")
    if decision == "REJECTED" and (not reason or not reason.strip()):
        raise HTTPException(status_code=422, detail="Reject reason required")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor_sub)
            _role(roles, DECIDE_ROLES)
            row = conn.execute(
                """SELECT id,status,version,created_by,assigned_to
                   FROM edarms_review_task
                   WHERE id=%s AND tenant_id=%s FOR UPDATE""",
                (task_id, tenant_id),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Task not found")
            try:
                check_decision(
                    ReviewTask(row["status"], row["version"], row["created_by"],
                               row["assigned_to"]),
                    actor_sub, expected_version,
                )
            except WorkspacePolicyError as exc:
                code = 409 if "version" in str(exc) or "already" in str(exc) else 403
                raise HTTPException(status_code=code, detail=str(exc)) from exc
            updated = conn.execute(
                """UPDATE edarms_review_task
                   SET status=%s, version=version+1, decided_by=%s,
                       decided_at=now(), decision_reason=%s
                   WHERE id=%s AND tenant_id=%s AND version=%s AND status='OPEN'
                   RETURNING id,status,version,decided_by,decided_at""",
                (decision, actor_sub, reason, task_id, tenant_id, expected_version),
            ).fetchone()
            if updated is None:
                raise HTTPException(status_code=409, detail="Concurrent decision")
            conn.execute(
                """INSERT INTO edarms_task_event
                   (tenant_id,task_id,actor_sub,action,reason)
                   VALUES (%s,%s,%s,%s,%s)""",
                (tenant_id, task_id, actor_sub, decision, reason),
            )
            return dict(updated)
