"""Tenant-scoped legal hold and disposition review vertical slice.

These workflows maintain evidence but NEVER destroy originals or authorize
production. Bank JRA evidence is provisioned by a separate trusted process.
"""
from datetime import date
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from fastapi import HTTPException

from services.workspace.store import _start_scope
from services.retention.decision import AppraisalFacts, appraisal_decision

VIEW_ROLES = frozenset({
    "records_officer", "records_manager", "approver", "legal_officer",
    "compliance_officer", "auditor",
})
HOLD_ROLES = frozenset({"legal_officer"})
PROPOSE_ROLES = frozenset({"records_officer", "records_manager"})
REVIEW_ROLES = frozenset({"records_manager"})
APPROVE_ROLES = frozenset({"approver"})


def _require(roles: set[str], allowed: frozenset[str]):
    if not roles.intersection(allowed):
        raise HTTPException(status_code=403, detail="Role not authorized for archival action")


def _record_lock(conn: psycopg.Connection, tenant_id: UUID, record_id: UUID):
    # All disposition transitions and scoped hold changes serialize per record.
    conn.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
        (f"edarms:{tenant_id}:{record_id}",),
    )


def _assess(conn: psycopg.Connection, tenant_id: UUID, record_id: UUID) -> dict:
    row = conn.execute(
        """SELECT r.status, r.vital_flag, r.retention_trigger_date,
                  r.retention_due_date, s.approval_status AS class_status,
                  j.approval_status AS jra_status, j.final_action AS jra_action,
                  j.legal_basis AS jra_basis, j.proposed_by AS jra_proposer,
                  j.approved_by AS jra_approver,
                  e.signed_approval_reference AS evidence_ref,
                  e.effective_from AS evidence_from,
                  e.effective_until AS evidence_until,
                  (SELECT count(*) FROM record_version v
                    WHERE v.tenant_id=r.tenant_id AND v.record_id=r.id)
                     AS version_count
           FROM record r
           JOIN record_class c ON c.tenant_id=r.tenant_id AND c.id=r.class_id
           JOIN classification_scheme s
                ON s.tenant_id=c.tenant_id AND s.id=c.scheme_id
           LEFT JOIN retention_rule j ON j.tenant_id=c.tenant_id
                                      AND j.id=c.retention_rule_id
           LEFT JOIN edarms_jra_evidence e
                ON e.tenant_id=j.tenant_id AND e.rule_id=j.id
           WHERE r.tenant_id=%s AND r.id=%s""",
        (tenant_id, record_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")
    hold_counts = conn.execute(
        """SELECT
           (SELECT count(DISTINCT h.id) FROM legal_hold h
            JOIN legal_hold_scope scope
             ON scope.tenant_id=h.tenant_id AND scope.hold_id=h.id
            WHERE h.tenant_id=%s AND h.status='ACTIVE'
              AND scope.record_id=%s),
           (SELECT count(DISTINCT h.id) FROM legal_hold h
            JOIN legal_hold_scope scope
             ON scope.tenant_id=h.tenant_id AND scope.hold_id=h.id
            WHERE h.tenant_id=%s AND h.status='ACTIVE'
              AND scope.saved_query IS NOT NULL)""",
        (tenant_id, record_id, tenant_id),
    ).fetchone()
    facts = AppraisalFacts(
        record_status=row["status"], record_is_vital=row["vital_flag"],
        trigger_date=row["retention_trigger_date"],
        due_date=row["retention_due_date"],
        version_count=row["version_count"],
        class_status=row["class_status"], jra_status=row["jra_status"],
        jra_action=row["jra_action"], jra_basis=row["jra_basis"],
        jra_proposer=row["jra_proposer"], jra_approver=row["jra_approver"],
        evidence_ref=row["evidence_ref"],
        evidence_effective_from=row["evidence_from"],
        evidence_effective_until=row["evidence_until"],
        active_record_holds=hold_counts[0],
        unresolved_tenant_query_holds=hold_counts[1],
    )
    return {
        **appraisal_decision(facts, date.today()),
        "tenant_id": str(tenant_id), "record_id": str(record_id),
        "active_hold_count": hold_counts[0],
        "unresolved_dynamic_holds": hold_counts[1],
        "evidence_registered": bool(row["evidence_ref"]),
    }


def record_appraisal(db: str, tenant_id: UUID, record_id: UUID, actor: str) -> dict:
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            _require(roles, VIEW_ROLES)
            return _assess(conn, tenant_id, record_id)


def apply_hold(db: str, tenant_id: UUID, record_id: UUID, actor: str,
               case_ref: str, legal_basis: str, reason: str) -> dict:
    if len(reason.strip()) < 4 or len(case_ref.strip()) < 2 or len(legal_basis.strip()) < 2:
        raise HTTPException(status_code=422, detail="Hold basis, case and reason required")
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            _require(roles, HOLD_ROLES)
            _record_lock(conn, tenant_id, record_id)
            found = conn.execute(
                "SELECT id FROM record WHERE tenant_id=%s AND id=%s",
                (tenant_id, record_id),
            ).fetchone()
            if not found:
                raise HTTPException(status_code=404, detail="Record not found")
            row = conn.execute(
                """INSERT INTO legal_hold
                   (tenant_id,case_ref,legal_basis,owner_sub,status)
                   VALUES(%s,%s,%s,%s,'ACTIVE') RETURNING id,status""",
                (tenant_id, case_ref, legal_basis, actor),
            ).fetchone()
            conn.execute(
                """INSERT INTO legal_hold_scope(tenant_id,hold_id,record_id)
                   VALUES(%s,%s,%s)""",
                (tenant_id, row["id"], record_id),
            )
            conn.execute(
                """INSERT INTO edarms_hold_event
                   (tenant_id,hold_id,record_id,actor_sub,action,reason)
                   VALUES(%s,%s,%s,%s,'APPLIED',%s)""",
                (tenant_id, row["id"], record_id, actor, reason),
            )
            return {"hold_id": str(row["id"]), "record_id": str(record_id),
                    "status": row["status"], "destruction_authorized": False}


def release_hold(db: str, tenant_id: UUID, hold_id: UUID, actor: str,
                 reason: str) -> dict:
    if len(reason.strip()) < 4:
        raise HTTPException(status_code=422, detail="Release evidence required")
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            _require(roles, HOLD_ROLES)
            lookup = conn.execute(
                """SELECT h.id,h.owner_sub,h.status,scope.record_id
                   FROM legal_hold h JOIN legal_hold_scope scope
                   ON scope.tenant_id=h.tenant_id AND scope.hold_id=h.id
                   WHERE h.tenant_id=%s AND h.id=%s
                     AND scope.record_id IS NOT NULL""",
                (tenant_id, hold_id),
            ).fetchall()
            if len(lookup) != 1:
                raise HTTPException(status_code=404, detail="Scoped hold not found")
            record_id = lookup[0]["record_id"]
            _record_lock(conn, tenant_id, record_id)
            hold = conn.execute(
                "SELECT owner_sub,status FROM legal_hold WHERE tenant_id=%s AND id=%s FOR UPDATE",
                (tenant_id, hold_id),
            ).fetchone()
            if hold["status"] != "ACTIVE":
                raise HTTPException(status_code=409, detail="Hold is not active")
            if hold["owner_sub"] == actor:
                raise HTTPException(status_code=403, detail="Independent hold release required")
            conn.execute(
                """UPDATE legal_hold SET status='RELEASED',
                   approved_by=%s,released_at=now()
                   WHERE tenant_id=%s AND id=%s""",
                (actor, tenant_id, hold_id),
            )
            conn.execute(
                """INSERT INTO edarms_hold_event
                   (tenant_id,hold_id,record_id,actor_sub,action,reason)
                   VALUES(%s,%s,%s,%s,'RELEASED',%s)""",
                (tenant_id, hold_id, record_id, actor, reason),
            )
            return {"hold_id": str(hold_id), "status": "RELEASED",
                    "destruction_authorized": False}


def propose_disposition(db: str, tenant_id: UUID, record_id: UUID,
                        actor: str, reason: str) -> dict:
    if len(reason.strip()) < 8:
        raise HTTPException(status_code=422, detail="Documented proposal reason required")
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            _require(roles, PROPOSE_ROLES)
            _record_lock(conn, tenant_id, record_id)
            appraisal = _assess(conn, tenant_id, record_id)
            if appraisal["state"] != "APPRAISAL_REVIEW_ONLY":
                raise HTTPException(
                    status_code=409, detail={"retention_blockers": appraisal["reasons"]}
                )
            result = conn.execute(
                """INSERT INTO edarms_disposition_case
                   (tenant_id,record_id,proposed_by,proposed_reason)
                   VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING
                   RETURNING id,status,version""",
                (tenant_id, record_id, actor, reason),
            ).fetchone()
            if result is None:
                raise HTTPException(status_code=409, detail="Existing open disposition case")
            conn.execute(
                """INSERT INTO edarms_disposition_event
                   (tenant_id,case_id,actor_sub,action,reason)
                   VALUES(%s,%s,%s,'PROPOSED',%s)""",
                (tenant_id, result["id"], actor, reason),
            )
            return _disposition_result(result, tenant_id)


def _disposition_result(case: dict, tenant_id: UUID) -> dict:
    return {
        "id": str(case["id"]), "tenant_id": str(tenant_id),
        "status": case["status"], "version": case["version"],
        "destruction_authorized": False,
        "physical_deletion_performed": False,
        "execution_gate": "BANK_JRA_LEGAL_SECURITY_PRODUCTION_SIGNOFF_REQUIRED",
    }


def decide_disposition(db: str, tenant_id: UUID, case_id: UUID, actor: str,
                       action: str, expected_version: int, reason: str) -> dict:
    if action not in ("REVIEWED", "APPROVED", "REJECTED"):
        raise HTTPException(status_code=422, detail="Unsupported disposition decision")
    if len(reason.strip()) < 4 or expected_version < 1:
        raise HTTPException(status_code=422, detail="Reason and version required")
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            _require(roles, APPROVE_ROLES if action == "APPROVED" else REVIEW_ROLES)
            target = conn.execute(
                "SELECT record_id FROM edarms_disposition_case WHERE tenant_id=%s AND id=%s",
                (tenant_id, case_id),
            ).fetchone()
            if target is None:
                raise HTTPException(status_code=404, detail="Disposition case not found")
            record_id = target["record_id"]
            _record_lock(conn, tenant_id, record_id)
            case = conn.execute(
                """SELECT id,record_id,status,version,proposed_by,reviewed_by
                   FROM edarms_disposition_case
                   WHERE tenant_id=%s AND id=%s FOR UPDATE""",
                (tenant_id, case_id),
            ).fetchone()
            if case is None:
                raise HTTPException(status_code=404, detail="Disposition case not found")
            if case["version"] != expected_version:
                raise HTTPException(status_code=409, detail="Stale disposition version")
            if action == "APPROVED" and case["status"] != "REVIEWED":
                raise HTTPException(status_code=409, detail="Independent review missing")
            if action in ("REVIEWED", "REJECTED") and case["status"] != "PROPOSED":
                raise HTTPException(status_code=409, detail="Case no longer proposed")
            if actor == case["proposed_by"] or actor == case["reviewed_by"]:
                raise HTTPException(status_code=403, detail="Independent decision required")
            appraisal = _assess(conn, tenant_id, record_id)
            if action != "REJECTED" and appraisal["state"] != "APPRAISAL_REVIEW_ONLY":
                raise HTTPException(
                    status_code=409, detail={"retention_blockers": appraisal["reasons"]}
                )
            # Fixed SQL statements keep both values AND identifiers out of string
            # interpolation; this also ensures the independent approval columns
            # cannot be selected via user-controlled values.
            if action == "APPROVED":
                result = conn.execute(
                    """UPDATE edarms_disposition_case
                       SET status=%s,version=version+1,
                           approved_by=%s,approved_at=now()
                       WHERE tenant_id=%s AND id=%s AND version=%s
                       RETURNING id,status,version""",
                    (action, actor, tenant_id, case_id, expected_version),
                ).fetchone()
            else:
                result = conn.execute(
                    """UPDATE edarms_disposition_case
                       SET status=%s,version=version+1,
                           reviewed_by=%s,reviewed_at=now()
                       WHERE tenant_id=%s AND id=%s AND version=%s
                       RETURNING id,status,version""",
                    (action, actor, tenant_id, case_id, expected_version),
                ).fetchone()
            if not result:
                raise HTTPException(status_code=409, detail="Concurrent disposition decision")
            conn.execute(
                """INSERT INTO edarms_disposition_event
                   (tenant_id,case_id,actor_sub,action,reason)
                   VALUES(%s,%s,%s,%s,%s)""",
                (tenant_id, case_id, actor, action, reason),
            )
            return _disposition_result(result, tenant_id)
