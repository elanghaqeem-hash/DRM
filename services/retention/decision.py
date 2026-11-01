"""Fail-closed appraisal decision support; never a license to destroy.

Legally binding retention durations, certificates and approvals belong to the
Bank, not a code generator. All policy-evidence values must be independently
verified by Bank Legal/Records before live use.
"""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AppraisalFacts:
    record_status: str
    record_is_vital: bool
    trigger_date: date | None
    due_date: date | None
    version_count: int
    class_status: str | None
    jra_status: str | None
    jra_action: str | None
    jra_basis: str | None
    jra_proposer: str | None
    jra_approver: str | None
    evidence_ref: str | None
    evidence_effective_from: date | None
    evidence_effective_until: date | None
    active_record_holds: int
    unresolved_tenant_query_holds: int


def appraisal_decision(facts: AppraisalFacts, as_of: date) -> dict:
    """Deterministically return blockers; even clean reviews cannot delete."""
    reasons = []
    if facts.record_status != "DECLARED":
        reasons.append("RECORD_NOT_DECLARED")
    if facts.record_is_vital:
        reasons.append("VITAL_RECORD_REVIEW_REQUIRED")
    if facts.version_count < 1:
        reasons.append("ORIGINAL_VERSION_MISSING")
    if facts.class_status != "APPROVED":
        reasons.append("CLASSIFICATION_NOT_APPROVED")
    if facts.trigger_date is None:
        reasons.append("RETENTION_TRIGGER_MISSING")
    if facts.due_date is None:
        reasons.append("RETENTION_DUE_MISSING")
    elif facts.due_date > as_of:
        reasons.append("RETENTION_NOT_DUE")
    if facts.jra_status != "APPROVED":
        reasons.append("JRA_NOT_APPROVED")
    if facts.jra_action != "DESTROY":
        reasons.append("NOT_DESTRUCTION_SERIES")
    if not facts.jra_basis or not facts.jra_basis.strip():
        reasons.append("JRA_LEGAL_BASIS_MISSING")
    if (not facts.jra_proposer or not facts.jra_approver
            or facts.jra_proposer == facts.jra_approver):
        reasons.append("JRA_INDEPENDENT_APPROVAL_MISSING")
    if not facts.evidence_ref:
        reasons.append("BANK_JRA_EVIDENCE_MISSING")
    if (facts.evidence_effective_from is None
            or facts.evidence_effective_from > as_of
            or (facts.evidence_effective_until is not None
                and facts.evidence_effective_until < as_of)):
        reasons.append("BANK_JRA_EVIDENCE_NOT_EFFECTIVE")
    if facts.active_record_holds:
        reasons.append("ACTIVE_LEGAL_HOLD")
    if facts.unresolved_tenant_query_holds:
        reasons.append("DYNAMIC_LEGAL_HOLD_UNRESOLVED")
    return {
        "state": "BLOCKED" if reasons else "APPRAISAL_REVIEW_ONLY",
        "reasons": reasons,
        "as_of": as_of.isoformat(),
        "physical_deletion_performed": False,
        "destruction_authorized": False,
        "bank_operational_signoff_verified": False,
    }
