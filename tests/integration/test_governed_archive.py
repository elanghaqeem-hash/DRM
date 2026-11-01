"""Real PostgreSQL integration: independent hold, JRA, disposal review, RLS.

ONLY disposable synthetic identities, records and JRA evidence. This test cannot
be used as evidence of Bank production sign-off, real destruction or real WORM.
"""
import os
from datetime import date, timedelta
from uuid import uuid4

import psycopg
import pytest
from fastapi import HTTPException

from services.retention.governed import (
    record_appraisal, apply_hold, release_hold,
    propose_disposition, decide_disposition,
)

pytestmark = pytest.mark.integration


def _seed():
    tenant, other, scheme, rule, cls, record_id, version = (uuid4() for _ in range(7))
    today = date.today()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.transaction():
            conn.execute(
                """INSERT INTO edarms_tenant(id,code,name) VALUES
                   (%s,%s,'Synthetic Bank A'),(%s,%s,'Synthetic Bank B')""",
                (tenant, "governed-" + tenant.hex[:12],
                 other, "governed-" + other.hex[:12]),
            )
            conn.cursor().executemany(
                """INSERT INTO edarms_membership
                   (tenant_id,actor_sub,role_code,enabled)
                   VALUES(%s,%s,%s,true)""",
                [
                    (tenant, "records-maker", "records_officer"),
                    (tenant, "records-reviewer", "records_manager"),
                    (tenant, "records-approver", "approver"),
                    (tenant, "legal-maker", "legal_officer"),
                    (tenant, "legal-checker", "legal_officer"),
                    (other, "outsider", "legal_officer"),
                ],
            )
            conn.execute(
                """INSERT INTO retention_rule
                   (id,tenant_id,code,version,trigger_type,final_action,
                    legal_basis,approval_status,proposed_by,approved_by)
                   VALUES(%s,%s,%s,1,'CLOSED','DESTROY',
                          'SYNTHETIC-TEST-ONLY','APPROVED','jra-maker','jra-checker')""",
                (rule, tenant, "JRA-" + rule.hex[:8]),
            )
            conn.execute(
                """INSERT INTO edarms_jra_evidence
                   (tenant_id,rule_id,signed_approval_reference,
                    approval_document_sha256,signatory_subject,verified_by,effective_from)
                   VALUES(%s,%s,'SYNTHETIC-TEST-NOT-BANK-APPROVAL',
                          %s,'test-signatory','test-independent-reviewer',%s)""",
                (tenant, rule, "a" * 64, today - timedelta(days=100)),
            )
            conn.execute(
                """INSERT INTO classification_scheme
                   (id,tenant_id,code,name,version,approval_status,
                    proposed_by,approved_by)
                   VALUES(%s,%s,%s,'Synthetic',1,'APPROVED','maker','checker')""",
                (scheme, tenant, "SCHEME-" + scheme.hex[:8]),
            )
            conn.execute(
                """INSERT INTO record_class
                   (id,tenant_id,scheme_id,code,name,required_metadata,
                    security_default,retention_rule_id)
                   VALUES(%s,%s,%s,%s,'Synthetic Series','{}','INTERNAL',%s)""",
                (cls, tenant, scheme, "SERIES-" + cls.hex[:8], rule),
            )
            conn.execute(
                """INSERT INTO record
                   (id,tenant_id,record_no,class_id,title,security_level,status,
                    owner_unit,created_by,retention_trigger_date,retention_due_date)
                   VALUES(%s,%s,%s,%s,'Synthetic record','INTERNAL',
                          'DECLARED','UNIT-TEST','synthetic-maker',%s,%s)""",
                (record_id, tenant, "EDARMS-" + record_id.hex, cls,
                 today - timedelta(days=200), today - timedelta(days=2)),
            )
            conn.execute(
                """INSERT INTO record_version
                   (id,tenant_id,record_id,major_version,object_key,mime,size_bytes,
                    sha256,created_by)
                   VALUES(%s,%s,%s,1,%s,'application/pdf',9,%s,'synthetic-maker')""",
                (version, tenant, record_id, "SYNTHETIC-NOT-REAL-WORM/" + version.hex,
                 "a" * 64),
            )
    return tenant, other, record_id, version


def test_review_blocked_by_multi_holds_and_permissions():
    tenant, other, record_id, version = _seed()
    url = os.environ["RUNTIME_DATABASE_URL"]
    appraisal = record_appraisal(url, tenant, record_id, "records-maker")
    assert appraisal["state"] == "APPRAISAL_REVIEW_ONLY"
    assert appraisal["destruction_authorized"] is False

    with pytest.raises(HTTPException) as denied:
        record_appraisal(url, tenant, record_id, "outsider")
    assert denied.value.status_code == 403
    with pytest.raises(HTTPException) as not_found:
        record_appraisal(url, other, record_id, "outsider")
    assert not_found.value.status_code == 404

    first = apply_hold(url, tenant, record_id, "legal-maker",
                       "SYN-CASE-1", "Synthetic test basis", "Test hold one")
    second = apply_hold(url, tenant, record_id, "legal-checker",
                        "SYN-CASE-2", "Synthetic test basis", "Test hold two")
    assert first["status"] == second["status"] == "ACTIVE"
    assert record_appraisal(url, tenant, record_id, "records-maker")[
        "active_hold_count"
    ] == 2

    with pytest.raises(HTTPException) as blocked:
        propose_disposition(url, tenant, record_id, "records-maker",
                            "Synthetic proposal must be blocked")
    assert blocked.value.status_code == 409
    assert "ACTIVE_LEGAL_HOLD" in blocked.value.detail["retention_blockers"]

    with pytest.raises(HTTPException) as self_release:
        release_hold(url, tenant, first["hold_id"], "legal-maker", "Self release")
    assert self_release.value.status_code == 403
    assert release_hold(url, tenant, first["hold_id"], "legal-checker",
                        "Independent review")["status"] == "RELEASED"
    assert record_appraisal(url, tenant, record_id, "records-maker")[
        "active_hold_count"
    ] == 1

    assert release_hold(url, tenant, second["hold_id"], "legal-maker",
                        "Another independent review")["status"] == "RELEASED"
    assert record_appraisal(url, tenant, record_id, "records-maker")[
        "state"
    ] == "APPRAISAL_REVIEW_ONLY"

    case = propose_disposition(url, tenant, record_id, "records-maker",
                               "Synthetic independently reviewed proposal")
    assert case["status"] == "PROPOSED"
    assert case["destruction_authorized"] is False
    with pytest.raises(HTTPException) as duplicate:
        propose_disposition(url, tenant, record_id, "records-maker",
                            "Duplicate pending request must be denied")
    assert duplicate.value.status_code == 409
    with pytest.raises(HTTPException) as wrong_actor:
        decide_disposition(url, tenant, case["id"], "records-maker",
                           "REVIEWED", 1, "Cannot self-review")
    assert wrong_actor.value.status_code == 403

    reviewed = decide_disposition(url, tenant, case["id"], "records-reviewer",
                                  "REVIEWED", 1, "Separate records reviewer")
    assert reviewed["status"] == "REVIEWED"
    approved = decide_disposition(url, tenant, case["id"], "records-approver",
                                  "APPROVED", 2, "Separate final reviewer")
    assert approved["status"] == "APPROVED"
    assert approved["physical_deletion_performed"] is False
    assert approved["destruction_authorized"] is False
    with pytest.raises(HTTPException) as stale:
        decide_disposition(url, tenant, case["id"], "records-approver",
                           "APPROVED", 2, "Stale approval")
    assert stale.value.status_code == 409

    with psycopg.connect(os.environ["DATABASE_URL"]) as admin:
        events = admin.execute(
            """SELECT action FROM edarms_disposition_event
               WHERE tenant_id=%s AND case_id=%s ORDER BY id""",
            (tenant, case["id"]),
        ).fetchall()
        assert [r[0] for r in events] == ["PROPOSED", "REVIEWED", "APPROVED"]
        with pytest.raises(psycopg.errors.RaiseException):
            with admin.transaction():
                admin.execute("DELETE FROM record_version WHERE id=%s", (version,))
        with pytest.raises(psycopg.errors.CheckViolation):
            with admin.transaction():
                admin.execute("UPDATE record SET status='DISPOSED' WHERE id=%s",
                              (record_id,))
        with pytest.raises(psycopg.errors.RaiseException):
            with admin.transaction():
                admin.execute(
                    "UPDATE record SET title='TAMPER' WHERE id=%s", (record_id,)
                )


def test_hold_applied_after_proposal_blocks_review():
    tenant, _, record_id, _ = _seed()
    url = os.environ["RUNTIME_DATABASE_URL"]
    proposal = propose_disposition(url, tenant, record_id, "records-maker",
                                   "Synthetic legitimate review proposal")
    apply_hold(url, tenant, record_id, "legal-maker", "LATE-CASE",
               "Synthetic late hold", "New hold after proposal")
    with pytest.raises(HTTPException) as stopped:
        decide_disposition(url, tenant, proposal["id"], "records-reviewer",
                           "REVIEWED", 1, "Must recheck hold before review")
    assert stopped.value.status_code == 409
    assert "ACTIVE_LEGAL_HOLD" in stopped.value.detail["retention_blockers"]


def test_jra_signoff_cannot_be_written_by_runtime():
    tenant, _, _, _ = _seed()
    with psycopg.connect(os.environ["RUNTIME_DATABASE_URL"]) as limited:
        with limited.transaction():
            limited.execute("SELECT set_config('edarms.tenant_id',%s,true)",
                            (str(tenant),))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with limited.transaction():
                    limited.execute(
                        """INSERT INTO edarms_jra_evidence
                           (tenant_id,rule_id,signed_approval_reference,
                            approval_document_sha256,signatory_subject,
                            verified_by,effective_from)
                           VALUES(%s,%s,'IMPOSSIBLE-CLIENT-SIGNOFF',%s,
                                  'forged','test',current_date)""",
                        (tenant, uuid4(), "a" * 64),
                    )
