"""Tenant isolation + idempotent generic review flow on disposable migrated PostgreSQL."""
import os
from uuid import uuid4
import psycopg
import pytest
from fastapi import HTTPException
from services.workspace.store import actor_workspace, create_task, decide_task, list_tasks


@pytest.mark.integration
def test_task_flow_tenant_isolation_and_maker_checker():
    url = os.environ["RUNTIME_DATABASE_URL"]
    admin_url = os.environ["DATABASE_URL"]
    a, b = uuid4(), uuid4()
    with psycopg.connect(admin_url) as conn:
        with conn.transaction():
            conn.execute(
                "INSERT INTO edarms_tenant(id,code,name) VALUES (%s,%s,%s),(%s,%s,%s)",
                (a, "t-" + a.hex[:12], "Synthetic A",
                 b, "t-" + b.hex[:12], "Synthetic B"),
            )
            conn.cursor().executemany(
                """INSERT INTO edarms_membership
                   (tenant_id,actor_sub,role_code,enabled)
                   VALUES (%s,%s,%s,true)""",
                [(a, "maker", "records_officer"), (a, "maker", "approver"),
                 (a, "checker", "approver"), (b, "outsider", "approver")],
            )
    rights = actor_workspace(url, a, "maker")
    assert rights["abilities"]["task_create"] is True
    assert rights["roles"] == ["approver", "records_officer"]

    created = create_task(url, a, "maker", "Synthetic review only",
                          "checker", "sandbox-key-001")
    assert created["status"] == "OPEN"
    assert created["idempotent_replay"] is False
    retry = create_task(url, a, "maker", "Synthetic review only",
                        "checker", "sandbox-key-001")
    assert retry["id"] == created["id"]
    assert retry["idempotent_replay"] is True

    with pytest.raises(HTTPException) as key_conflict:
        create_task(url, a, "maker", "Changed payload", "checker", "sandbox-key-001")
    assert key_conflict.value.status_code == 409

    with pytest.raises(HTTPException) as cross_tenant:
        list_tasks(url, a, "outsider")
    assert cross_tenant.value.status_code == 403
    assert list_tasks(url, b, "outsider")["items"] == []
    assert len(list_tasks(url, a, "checker")["items"]) == 1

    with pytest.raises(HTTPException) as self_approve:
        decide_task(url, a, created["id"], "maker", "APPROVED", 1, None)
    assert self_approve.value.status_code == 403
    with pytest.raises(HTTPException) as no_reason:
        decide_task(url, a, created["id"], "checker", "REJECTED", 1, "")
    assert no_reason.value.status_code == 422

    approved = decide_task(url, a, created["id"], "checker", "APPROVED", 1, "Reviewed")
    assert approved["status"] == "APPROVED"
    assert approved["version"] == 2
    with pytest.raises(HTTPException) as stale:
        decide_task(url, a, created["id"], "checker", "APPROVED", 1, None)
    assert stale.value.status_code == 409

    with psycopg.connect(url) as conn:
        with conn.transaction():
            # CI seed user is a superuser, which bypasses RLS even with FORCE.
            # Switch into PostgreSQL built-in read-only NON-BYPASSRLS role.
            conn.execute("SET LOCAL ROLE pg_read_all_data")
            bypass = conn.execute(
                "SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user"
            ).fetchone()[0]
            assert bypass is False
            conn.execute("SELECT set_config('edarms.tenant_id', %s, true)", (str(b),))
            hidden = conn.execute(
                "SELECT id FROM edarms_review_task WHERE id=%s", (created["id"],)
            ).fetchall()
            assert hidden == []
        with conn.transaction():
            conn.execute("SELECT set_config('edarms.tenant_id', %s, true)", (str(a),))
            actions = conn.execute(
                "SELECT action FROM edarms_task_event WHERE task_id=%s ORDER BY id",
                (created["id"],),
            ).fetchall()
            assert [r[0] for r in actions] == ["CREATED", "APPROVED"]
