"""Retention previews always deny destruction and respect multi-hold."""
from datetime import date, timedelta

from services.retention.eligibility import RetentionFacts, appraisal_preview


TODAY = date(2026, 10, 31)


def baseline(**changes):
    fields = dict(
        status="DECLARED", due_date=TODAY - timedelta(days=1),
        trigger_date=TODAY - timedelta(days=365), rule_status="APPROVED",
        rule_basis="Synthetic only (not legal authorization)", proposer="p",
        approver="q", final_action="DESTROY", active_hold_count=0,
    )
    fields.update(changes)
    return RetentionFacts(**fields)


def test_appraisal_is_never_destruction_authority():
    result = appraisal_preview(baseline(), TODAY)
    assert result["state"] == "APPRAISAL_REVIEW_ONLY"
    assert result["destruction_authorized"] is False
    assert result["bank_jra_legal_signoff_verified"] is False


def test_hold_still_blocks_when_other_hold_released():
    assert "ACTIVE_LEGAL_HOLD" in appraisal_preview(
        baseline(active_hold_count=1), TODAY
    )["reasons"]


def test_dynamic_hold_blocks_all_tenant_disposal_in_poc():
    assert "DYNAMIC_LEGAL_HOLD_UNRESOLVED" in appraisal_preview(
        baseline(unresolved_query_holds=1), TODAY
    )["reasons"]


def test_retention_event_missing_blocks():
    assert "RETENTION_TRIGGER_MISSING" in appraisal_preview(
        baseline(trigger_date=None), TODAY
    )["reasons"]


def test_unapproved_jra_blocks():
    assert "NO_APPROVED_JRA" in appraisal_preview(
        baseline(rule_status="DRAFT"), TODAY
    )["reasons"]


def test_permanent_blocks():
    assert "PERMANENT_OR_VITAL_REVIEW_REQUIRED" in appraisal_preview(
        baseline(permanent=True), TODAY
    )["reasons"]


def test_expiry_future_blocks():
    assert "RETENTION_NOT_DUE" in appraisal_preview(
        baseline(due_date=TODAY + timedelta(days=1)), TODAY
    )["reasons"]


def test_maker_checker_and_basis_required():
    reasons = appraisal_preview(
        baseline(proposer="same", approver="same", rule_basis=""), TODAY
    )["reasons"]
    assert "JRA_MAKER_CHECKER_MISSING" in reasons
    assert "LEGAL_BASIS_UNVERIFIED" in reasons


def test_non_destroy_action_blocks():
    assert "RULE_NOT_DESTRUCTION" in appraisal_preview(
        baseline(final_action="PERMANENT"), TODAY
    )["reasons"]


def test_exception_blocks():
    assert "OPEN_LEGAL_OR_RETENTION_EXCEPTION" in appraisal_preview(
        baseline(unresolved_exception=True), TODAY
    )["reasons"]
