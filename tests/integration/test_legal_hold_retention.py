"""PostgreSQL 16 end-to-end synthetic legal hold and retention control tests."""
import os
from datetime import date, timedelta
from uuid import uuid4

import psycopg
from psycopg import sql
from infra.scripts.provision_runtime import provision
from psycopg.conninfo import make_conninfo
import pytest
from fastapi import HTTPException

from services.records.isolation import (
    apply_legal_hold, release_legal_hold, retention_preview,
)


@pytest.fixture
def sandbox_db_role(monkeypatch):
    """Exercise the REAL least-privilege provisioning script in CI."""
    url = os.environ["DATABASE_URL"]
    name = "edarms_ci_" + uuid4().hex[:12]
    secret = uuid4().hex + uuid4().hex
    monkeypatch.setenv("APP_DB_USER", name)
    monkeypatch.setenv("APP_DB_PASSWORD", secret)
    monkeypatch.setenv("DATABASE_URL", url)
    provision()
    try:
        yield url, make_conninfo(url, user=name, password=secret)
    finally:
        with psycopg.connect(url, autocommit=True) as admin:
            # DROP OWNED only revokes this test role's grants; it owns no tables.
            admin.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(name)))
            admin.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(name)))


@pytest.mark.integration
def test_legal_hold_multi_scope_and_independent_release(sandbox_db_role):
    bootstrap, runtime = sandbox_db_role
    tenant_a, tenant_b = uuid4(), uuid4()
    scheme, series, record_id = uuid4(), uuid4(), uuid4()
    with psycopg.connect(bootstrap) as conn:
        with conn.transaction():
            conn.execute(
                "INSERT INTO edarms_tenant(id,code,name) VALUES (%s,%s,%s),(%s,%s,%s)",
                (tenant_a, "hold-" + tenant_a.hex[:12], "Synthetic Hold A",
                 tenant_b, "hold-" + tenant_b.hex[:12], "Synthetic Hold B"),
            )
            conn.cursor().executemany(
                """INSERT INTO edarms_membership
                (tenant_id,actor_sub,role_code,enabled) VALUES (%s,%s,%s,true)""",
                [(tenant_a, "records", "records_manager"),
                 (tenant_a, "legal-maker", "legal_officer"),
                 (tenant_a, "legal-checker", "legal_officer"),
                 (tenant_b, "other", "legal_officer")],
            )
            rule = uuid4()
            conn.execute(
                """INSERT INTO retention_rule
                (id,tenant_id,code,version,trigger_type,final_action,legal_basis,
                 approval_status,proposed_by,approved_by)
                VALUES (%s,%s,'DEMO',1,'CLOSED','DESTROY','SYNTHETIC-ONLY',
                        'APPROVED','maker','checker')""",
                (rule, tenant_a),
            )
            conn.execute(
                """INSERT INTO classification_scheme
                (id,tenant_id,code,name,version,approval_status,proposed_by,approved_by)
                VALUES (%s,%s,'DEMO','Synthetic scheme',1,'APPROVED','maker','checker')""",
                (scheme, tenant_a),
            )
            conn.execute(
                """INSERT INTO record_class
                (id,tenant_id,scheme_id,code,name,security_default,retention_rule_id)
                VALUES (%s,%s,%s,'DEMO','Synthetic class','INTERNAL',%s)""",
                (series, tenant_a, scheme, rule),
            )
            conn.execute(
                """INSERT INTO record
                (id,tenant_id,record_no,class_id,title,security_level,owner_unit,
                 created_by,status,retention_trigger_date,retention_due_date)
                VALUES (%s,%s,'SYN-001',%s,'Synthetic record','INTERNAL','TEST',
                       'maker','DECLARED',%s,%s)""",
                (record_id, tenant_a, series,
                 date.today() - timedelta(days=365),
                 date.today() - timedelta(days=2)),
            )
    with pytest.raises(HTTPException) as unsafe:
        retention_preview(bootstrap, tenant_a, record_id, "records")
    assert unsafe.value.status_code == 503

    preview = retention_preview(runtime, tenant_a, record_id, "records")
    assert preview["state"] == "APPRAISAL_REVIEW_ONLY"
    assert preview["destruction_authorized"] is False
    with pytest.raises(HTTPException) as other:
        retention_preview(runtime, tenant_b, record_id, "other")
    assert other.value.status_code in (403, 404)

    first = apply_legal_hold(
        runtime, tenant_a, record_id, "legal-maker",
        "case-a", "SYNTHETIC", "Synthetic court hold A",
    )
    second = apply_legal_hold(
        runtime, tenant_a, record_id, "legal-checker",
        "case-b", "SYNTHETIC", "Synthetic regulator hold B",
    )
    assert second["status"] == "ACTIVE"
    blocked = retention_preview(runtime, tenant_a, record_id, "records")
    assert blocked["state"] == "BLOCKED"
    assert "ACTIVE_LEGAL_HOLD" in blocked["reasons"]
    with pytest.raises(HTTPException) as self_release:
        release_legal_hold(
            runtime, tenant_a, first["hold_id"], "legal-maker", "Cannot self release"
        )
    assert self_release.value.status_code == 403

    released = release_legal_hold(
        runtime, tenant_a, first["hold_id"], "legal-checker", "Independent evidence"
    )
    assert released["status"] == "RELEASED"
    assert "ACTIVE_LEGAL_HOLD" in retention_preview(
        runtime, tenant_a, record_id, "records"
    )["reasons"]

    with psycopg.connect(bootstrap) as conn:
        history = conn.execute(
            """SELECT action FROM edarms_legal_hold_event
               WHERE tenant_id=%s AND hold_id=%s ORDER BY id""",
            (tenant_a, first["hold_id"]),
        ).fetchall()
        assert [row[0] for row in history] == ["APPLIED", "RELEASED"]
        with conn.transaction():
            with pytest.raises(psycopg.errors.CheckViolation):
                with conn.transaction():
                    conn.execute(
                        "UPDATE record SET status='DISPOSED' WHERE id=%s",
                        (record_id,),
                    )
