"""Sprint 1 foundation: control-driven metadata and record state invariants.

The Bank owns all classes, required fields, retention durations and numbering.
No user may bypass a published classification or edit a declared record.
"""


class RecordPolicyViolation(ValueError):
    """Domain-level policy rejection, to be mapped to an audited API rejection."""


def require_approved_scheme(approval_status: str) -> None:
    if approval_status != "APPROVED":
        raise RecordPolicyViolation("Classification scheme has not been approved")


def verify_maker_checker(proposed_by: str, approved_by: str) -> None:
    if not proposed_by or not approved_by or proposed_by == approved_by:
        raise RecordPolicyViolation("Distinct proposer and approver required")


def validate_required_metadata(metadata: dict, configuration: dict) -> None:
    """Configuration format: {'required_fields': ['field_name', ...]}.

    In Sprint 1, this list comes exclusively from the approved record_class
    definition. A missing or malformed configuration FAILS CLOSED.
    """
    required = configuration.get("required_fields")
    if not isinstance(required, list) or any(
        not isinstance(key, str) or not key.strip() for key in required
    ):
        raise RecordPolicyViolation("Invalid required-metadata configuration")
    if not required:
        raise RecordPolicyViolation("No approved mandatory-metadata fields configured")
    missing = [
        key for key in required
        if key not in metadata or metadata[key] is None
        or (isinstance(metadata[key], str) and not metadata[key].strip())
    ]
    if missing:
        raise RecordPolicyViolation("Missing mandatory metadata: " + ", ".join(sorted(missing)))


def assert_content_editable(record_status: str) -> None:
    if record_status != "DRAFT":
        raise RecordPolicyViolation("Declared, held or disposed record content is immutable")


def assert_can_declare(record_status: str, version_count: int) -> None:
    assert_content_editable(record_status)
    if version_count < 1:
        raise RecordPolicyViolation("A record requires a stored version before declaration")
