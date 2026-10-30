"""Tenant-scoped read-only retention previews and legal holds (synthetic PoC).

No destruction or JRA publication endpoint. DB runtime account must be a
non-superuser, non-BYPASSRLS identity distinct from migration/table owner.
"""
from datetime import date, timezone, datetime
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from fastapi import HTTPException

from services.retention.eligibility import RetentionFacts, appraisal_preview
from services.workspace.store import _start_scope


def _verified_runtime(conn):
    row = conn.execute(
        """SELECT r.rolsuper,r.rolbypassrls,
                  (SELECT pg_get_userbyid(c.relowner) FROM pg_class c
                   WHERE c.oid='public.record'::regclass) AS owner
           FROM pg_roles r WHERE r.rolname=current_user"""
    ).fetchone()
    if not row or row["rolsuper"] or row["rolbypassrls"] or row["owner"] == conn.execute(
        "SELECT current_user"
    ).fetchone()["current_user"]:
        raise HTTPException(
            status_code=503,
            detail="Unsafe DB application identity: use non-owner NO-BYPASSRLS runtime role",
        )


def _tenant_role(conn, tenant_id, actor, required):
    _verified_runtime(conn)
    roles = _start_scope(conn, tenant_id, actor)
    if not roles.intersection(required):
        raise HTTPException(status_code=403, detail="Tenant-scoped role is required")


def retention_preview(database_url: str, tenant_id: UUID, record_id: UUID, actor: str) -> dict:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            _tenant_role(
                conn, tenant_id, actor,
                {"records_manager", "records_officer", "legal_officer", "auditor"},
            )
            row = conn.execute(
                """SELECT rec.id, rec.status, rec.retention_trigger_date,
                          rec.retention_due_date,rec.vital_flag,
                          rule.approval_status AS rule_status,
                          rule.legal_basis AS rule_basis,rule.proposed_by,rule.approved_by,
                          rule.final_action
                   FROM record rec
                   JOIN record_class cls
                     ON cls.tenant_id=rec.tenant_id AND cls.id=rec.class_id
                   LEFT JOIN retention_rule rule
                     ON rule.tenant_id=cls.tenant_id AND rule.id=cls.retention_rule_id
                   WHERE rec.tenant_id=%s AND rec.id=%s""",
                (tenant_id, record_id),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Record not found")
            holds = conn.execute(
                """SELECT
                     count(*) FILTER (WHERE scope.record_id=%s) AS direct,
                     count(*) FILTER (WHERE scope.saved_query IS NOT NULL) AS dynamic
                   FROM legal_hold_scope scope
                   JOIN legal_hold h
                    ON h.tenant_id=scope.tenant_id AND h.id=scope.hold_id
                   WHERE scope.tenant_id=%s AND h.status IN ('ACTIVE','REVIEW')""",
                (record_id, tenant_id),
            ).fetchone()
            result = appraisal_preview(
                RetentionFacts(
                    status=row["status"],
                    trigger_date=row["retention_trigger_date"],
                    due_date=row["retention_due_date"],
                    rule_status=row["rule_status"],
                    rule_basis=row["rule_basis"],
                    proposer=row["proposed_by"],
                    approver=row["approved_by"],
                    final_action=row["final_action"],
                    active_hold_count=holds["direct"],
                    unresolved_query_holds=holds["dynamic"],
                    permanent=row["vital_flag"],
                ),
                date.today(),
            )
            # Event payload only records reason codes; no confidential metadata.
            conn.execute(
                """INSERT INTO edarms_archive_control_event
                   (tenant_id,record_id,actor_sub,event_type,details)
                   VALUES (%s,%s,%s,'RETENTION_PREVIEW',%s::jsonb)""",
                (tenant_id, record_id, actor,
                 __import__("json").dumps({"state": result["state"],
                                          "reasons": result["reasons"]})),
            )
            return {"record_id": str(record_id), **result}


def apply_legal_hold(
    database_url: str, tenant_id: UUID, record_id: UUID, actor: str,
    case_ref: str, legal_basis: str, reason: str,
) -> dict:
    if not all((case_ref.strip(), legal_basis.strip(), reason.strip())):
        raise HTTPException(status_code=422, detail="Case, legal basis and reason required")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            _tenant_role(conn, tenant_id, actor, {"legal_officer"})
            record = conn.execute(
                """SELECT id,status FROM record
                   WHERE id=%s AND tenant_id=%s FOR UPDATE""",
                (record_id, tenant_id),
            ).fetchone()
            if not record:
                raise HTTPException(status_code=404, detail="Record not found")
            if record["status"] == "DISPOSED":
                raise HTTPException(status_code=409, detail="Already disposed")
            exists = conn.execute(
                "SELECT id FROM legal_hold WHERE tenant_id=%s AND case_ref=%s",
                (tenant_id, case_ref),
            ).fetchone()
            if exists:
                raise HTTPException(status_code=409, detail="Case reference already exists")
            hold = conn.execute(
                """INSERT INTO legal_hold (tenant_id,case_ref,legal_basis,owner_sub,status)
                   VALUES (%s,%s,%s,%s,'ACTIVE') RETURNING id,status""",
                (tenant_id, case_ref, legal_basis, actor),
            ).fetchone()
            conn.execute(
                "INSERT INTO legal_hold_scope(tenant_id,hold_id,record_id) VALUES (%s,%s,%s)",
                (tenant_id, hold["id"], record_id),
            )
            conn.execute(
                """INSERT INTO edarms_legal_hold_event
                   (tenant_id,hold_id,actor_sub,action,reason)
                   VALUES (%s,%s,%s,'APPLIED',%s)""",
                (tenant_id, hold["id"], actor, reason),
            )
            return {"hold_id": str(hold["id"]), "record_id": str(record_id),
                    "status": "ACTIVE"}


def release_legal_hold(
    database_url: str, tenant_id: UUID, hold_id: UUID, actor: str, reason: str,
) -> dict:
    if not reason.strip():
        raise HTTPException(status_code=422, detail="Release reason required")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            _tenant_role(conn, tenant_id, actor, {"legal_officer"})
            hold = conn.execute(
                """SELECT id,status,owner_sub FROM legal_hold
                   WHERE tenant_id=%s AND id=%s FOR UPDATE""",
                (tenant_id, hold_id),
            ).fetchone()
            if not hold:
                raise HTTPException(status_code=404, detail="Hold not found")
            if hold["owner_sub"] == actor:
                raise HTTPException(status_code=403, detail="Independent releaser required")
            if hold["status"] == "RELEASED":
                raise HTTPException(status_code=409, detail="Hold already released")
            conn.execute(
                """UPDATE legal_hold SET status='RELEASED',
                   released_at=now(),approved_by=%s
                   WHERE tenant_id=%s AND id=%s""",
                (actor, tenant_id, hold_id),
            )
            conn.execute(
                """INSERT INTO edarms_legal_hold_event
                   (tenant_id,hold_id,actor_sub,action,reason)
                   VALUES (%s,%s,%s,'RELEASED',%s)""",
                (tenant_id, hold_id, actor, reason),
            )
            return {"hold_id": str(hold_id), "status": "RELEASED"}
