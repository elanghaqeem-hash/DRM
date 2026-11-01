"""Executable synthetic appraisal policy tests; zero real JRA approvals."""
from datetime import date, timedelta
from dataclasses import replace

from services.retention.decision import AppraisalFacts, appraisal_decision

TODAY = date(2026, 11, 1)


def complete():
    return AppraisalFacts(
        record_status="DECLARED", record_is_vital=False,
        trigger_date=TODAY - timedelta(days=200),
        due_date=TODAY - timedelta(days=1),
        version_count=1, class_status="APPROVED", jra_status="APPROVED",
        jra_action="DESTROY", jra_basis="Synthetic legal basis for tests",
        jra_proposer="synthetic-maker", jra_approver="synthetic-checker",
        evidence_ref="SYNTHETIC-NOT-A-BANK-SIGNATURE",
        evidence_effective_from=TODAY - timedelta(days=100),
        evidence_effective_until=None, active_record_holds=0,
        unresolved_tenant_query_holds=0,
    )


def test_clean_appraisal_never_authorizes_deletion():
    decision = appraisal_decision(complete(), TODAY)
    assert decision["state"] == "APPRAISAL_REVIEW_ONLY"
    assert decision["reasons"] == []
    assert decision["destruction_authorized"] is False
    assert decision["physical_deletion_performed"] is False
    assert decision["bank_operational_signoff_verified"] is False


def test_unapproved_policy_fails_closed():
    decision = appraisal_decision(replace(
        complete(), jra_status="DRAFT", evidence_ref=None,
        jra_proposer="same", jra_approver="same",
    ), TODAY)
    assert decision["state"] == "BLOCKED"
    assert "JRA_NOT_APPROVED" in decision["reasons"]
    assert "BANK_JRA_EVIDENCE_MISSING" in decision["reasons"]
    assert "JRA_INDEPENDENT_APPROVAL_MISSING" in decision["reasons"]


def test_multiple_holds_and_query_scope_block():
    outcome = appraisal_decision(replace(
        complete(), active_record_holds=2, unresolved_tenant_query_holds=1,
    ), TODAY)
    assert "ACTIVE_LEGAL_HOLD" in outcome["reasons"]
    assert "DYNAMIC_LEGAL_HOLD_UNRESOLVED" in outcome["reasons"]


def test_retention_in_future_or_untriggered_blocks():
    outcome = appraisal_decision(replace(
        complete(), trigger_date=None, due_date=TODAY + timedelta(days=1),
    ), TODAY)
    assert "RETENTION_TRIGGER_MISSING" in outcome["reasons"]
    assert "RETENTION_NOT_DUE" in outcome["reasons"]


def test_vital_missing_original_and_unapproved_scheme_blocks():
    outcome = appraisal_decision(replace(
        complete(), record_is_vital=True, version_count=0, class_status="DRAFT",
    ), TODAY)
    assert "VITAL_RECORD_REVIEW_REQUIRED" in outcome["reasons"]
    assert "ORIGINAL_VERSION_MISSING" in outcome["reasons"]
    assert "CLASSIFICATION_NOT_APPROVED" in outcome["reasons"]


def test_expired_policy_evidence_and_non_destroy_action_blocks():
    outcome = appraisal_decision(replace(
        complete(), evidence_effective_until=TODAY - timedelta(days=1),
        jra_action="PERMANENT",
    ), TODAY)
    assert "BANK_JRA_EVIDENCE_NOT_EFFECTIVE" in outcome["reasons"]
    assert "NOT_DESTRUCTION_SERIES" in outcome["reasons"]
