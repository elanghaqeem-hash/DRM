"""Tenant-scoped audit ledger tests on disposable migrated PostgreSQL."""
import os
from uuid import uuid4
import pytest
import psycopg
from fastapi import HTTPException
from services.audit.store import append_event, verify_chain

pytestmark = pytest.mark.integration


def test_audit_write_and_mutation_denied():
    admin_url = os.environ["DATABASE_URL"]
    url = os.environ["RUNTIME_DATABASE_URL"]
    a, b = uuid4(), uuid4()
    with psycopg.connect(admin_url) as connection:
        with connection.transaction():
            connection.execute(
                "INSERT INTO edarms_tenant (id,code,name) VALUES "
                "(%s,%s,'Synthetic A'),(%s,%s,'Synthetic B')",
                (a, "audit-" + a.hex[:12], b, "audit-" + b.hex[:12]),
            )
            connection.execute(
                "INSERT INTO edarms_membership "
                "(tenant_id,actor_sub,role_code,enabled) "
                "VALUES (%s,'fictitious-actor','auditor',true)",
                (a,),
            )
    row = append_event(
        url, tenant_id=a, actor_sub="fictitious-actor", actor_role="audit_writer",
        source_ip="127.0.0.1", device=None, action="CREATE",
        object_ref="SYNTHETIC-TEST-ONLY", before_hash=None, after_hash=None, result="SUCCESS",
    )
    report = verify_chain(url, tenant_id=a, actor_sub="fictitious-actor")
    assert report["valid"] and row["event_hash"] == report["head_hash"]
    assert report["events_checked"] == 1
    assert not report["external_anchor_verified"]
    with pytest.raises(HTTPException) as denied:
        verify_chain(url, tenant_id=b, actor_sub="fictitious-actor")
    assert denied.value.status_code == 403
    # Only the admin fixture can inspect an unscoped row; even DBA cannot
    # silently update it because of the append-only trigger.
    with psycopg.connect(admin_url) as connection:
        with pytest.raises(psycopg.errors.RaiseException):
            connection.execute(
                "UPDATE audit_event SET action='ALTERED' WHERE seq=%s", (row["seq"],)
            )
