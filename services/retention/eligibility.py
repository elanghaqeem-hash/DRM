"""Deterministic, FAIL-CLOSED retention appraisal preview.

A positive review outcome is NEVER permission to destroy. Approved Bank JRA
and a separate independent disposal workflow are mandatory production gates.
"""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class RetentionFacts:
    status: str
    due_date: date | None
    trigger_date: date | None
    rule_status: str | None
    rule_basis: str | None
    proposer: str | None
    approver: str | None
    final_action: str | None
    active_hold_count: int
    unresolved_query_holds: int = 0
    permanent: bool = False
    unresolved_exception: bool = False


def appraisal_preview(facts: RetentionFacts, as_of: date) -> dict:
    """Return auditable reasons, not a boolean authorization to execute deletion."""
    reasons: list[str] = []
    if facts.status != "DECLARED":
        reasons.append("RECORD_NOT_DECLARED_OR_ALREADY_DISPOSED")
    if facts.permanent:
        reasons.append("PERMANENT_OR_VITAL_REVIEW_REQUIRED")
    if facts.trigger_date is None:
        reasons.append("RETENTION_TRIGGER_MISSING")
    if facts.due_date is None:
        reasons.append("RETENTION_DUE_DATE_MISSING")
    elif facts.due_date > as_of:
        reasons.append("RETENTION_NOT_DUE")
    if facts.rule_status != "APPROVED":
        reasons.append("NO_APPROVED_JRA")
    if not facts.rule_basis or not facts.rule_basis.strip():
        reasons.append("LEGAL_BASIS_UNVERIFIED")
    if not facts.proposer or not facts.approver or facts.proposer == facts.approver:
        reasons.append("JRA_MAKER_CHECKER_MISSING")
    if facts.final_action != "DESTROY":
        reasons.append("RULE_NOT_DESTRUCTION")
    if facts.active_hold_count:
        reasons.append("ACTIVE_LEGAL_HOLD")
    if facts.unresolved_query_holds:
        # A dynamic hold query is not evaluated by this prototype;
        # conservatively block ALL disposal within the tenant.
        reasons.append("DYNAMIC_LEGAL_HOLD_UNRESOLVED")
    if facts.unresolved_exception:
        reasons.append("OPEN_LEGAL_OR_RETENTION_EXCEPTION")
    return {
        "state": "BLOCKED" if reasons else "APPRAISAL_REVIEW_ONLY",
        "reasons": reasons,
        "as_of": as_of.isoformat(),
        "destruction_authorized": False,
        "bank_jra_legal_signoff_verified": False,
    }
