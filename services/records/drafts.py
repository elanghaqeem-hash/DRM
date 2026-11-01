"""WP02: real tenant-scoped controlled draft records, no fake declaration.

Only classifications approved by Bank-owned governance can create a DRAFT.
No scanned original, permanent record number, immutable declaration or access
to Bank records is claimed by this limited synthetic integration slice.
"""
import json
from hashlib import sha256
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from fastapi import HTTPException

from services.records.domain import RecordPolicyViolation, validate_required_metadata
from services.workspace.store import _start_scope

CREATE_ROLES = frozenset({"records_officer", "records_manager"})
VIEW_ROLES = frozenset({"records_officer", "records_manager", "auditor"})


def list_approved_classes(db: str, tenant_id: UUID, actor: str) -> dict:
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            if not roles.intersection(VIEW_ROLES):
                raise HTTPException(status_code=403, detail="Records access not granted")
            rows = conn.execute(
                """SELECT c.id,c.code,c.name,c.security_default,c.required_metadata,
                          c.retention_rule_id
                   FROM record_class c JOIN classification_scheme s
                     ON s.tenant_id=c.tenant_id AND s.id=c.scheme_id
                   WHERE c.tenant_id=%s AND s.approval_status='APPROVED'
                   ORDER BY c.code LIMIT 200""",
                (tenant_id,),
            ).fetchall()
            return {"tenant_id": str(tenant_id), "items": [dict(row) for row in rows],
                    "release_scope": "WP02_PARTIAL_SYNTHETIC_POC"}


def create_controlled_draft(db: str, tenant_id: UUID, class_id: UUID,
                            actor: str, title: str, owner_unit: str,
                            metadata: dict) -> dict:
    if (not title.strip() or title != title.strip() or len(title) > 300
            or not owner_unit.strip() or len(owner_unit) > 200):
        raise HTTPException(status_code=422, detail="Title and owner unit required")
    if not isinstance(metadata, dict):
        raise HTTPException(status_code=422, detail="Metadata must be JSON object")
    with psycopg.connect(db, row_factory=dict_row) as conn:
        with conn.transaction():
            roles = _start_scope(conn, tenant_id, actor)
            if not roles.intersection(CREATE_ROLES):
                raise HTTPException(status_code=403, detail="Records officer required")
            schema = conn.execute(
                """SELECT c.required_metadata,c.security_default,
                          s.approval_status
                   FROM record_class c JOIN classification_scheme s
                    ON s.tenant_id=c.tenant_id AND s.id=c.scheme_id
                   WHERE c.tenant_id=%s AND c.id=%s""",
                (tenant_id, class_id),
            ).fetchone()
            if not schema:
                raise HTTPException(status_code=404, detail="Classification not found")
            if schema["approval_status"] != "APPROVED":
                raise HTTPException(status_code=409, detail="Classification not approved")
            try:
                validate_required_metadata(metadata, schema["required_metadata"])
            except RecordPolicyViolation as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            record_id = uuid4()
            provisional_no = "DRAFT-" + record_id.hex
            result = conn.execute(
                """INSERT INTO record
                   (id,tenant_id,record_no,class_id,title,security_level,status,
                    owner_unit,metadata,created_by)
                   VALUES(%s,%s,%s,%s,%s,%s,'DRAFT',%s,%s,%s)
                   RETURNING id,record_no,status,created_at""",
                (record_id, tenant_id, provisional_no, class_id, title,
                 schema["security_default"], owner_unit, Jsonb(metadata), actor),
            ).fetchone()
            # Only the digest is written to the append-only event, not PII.
            digest = sha256(json.dumps(
                metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            ).encode("utf-8")).hexdigest()
            conn.execute(
                """INSERT INTO edarms_draft_event
                   (tenant_id,record_id,actor_sub,event_type,metadata_sha256)
                   VALUES(%s,%s,%s,'DRAFT_CREATED',%s)""",
                (tenant_id, record_id, actor, digest),
            )
            return {
                "id": str(result["id"]), "tenant_id": str(tenant_id),
                "record_no": result["record_no"], "status": result["status"],
                "classification_id": str(class_id),
                "content_declared": False,
                "original_storage_verified": False,
                "release_scope": "WP02_DRAFT_ONLY",
            }
