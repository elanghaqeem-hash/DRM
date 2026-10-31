import pytest
from services.records.domain import (
    RecordPolicyViolation, assert_can_declare, assert_content_editable,
    require_approved_scheme, validate_required_metadata, verify_maker_checker,
)


def test_reject_unapproved_scheme():
    with pytest.raises(RecordPolicyViolation):
        require_approved_scheme("DRAFT")


def test_allow_approved_scheme():
    require_approved_scheme("APPROVED")


def test_segregation_of_duties():
    with pytest.raises(RecordPolicyViolation):
        verify_maker_checker("employee-one", "employee-one")
    verify_maker_checker("employee-one", "employee-two")


def test_dynamic_metadata_required():
    config = {"required_fields": ["document_date", "owner_unit"]}
    with pytest.raises(RecordPolicyViolation, match="owner_unit"):
        validate_required_metadata({"document_date": "2026-10-30"}, config)
    validate_required_metadata({"document_date": "2026-10-30", "owner_unit": "TEST"}, config)


def test_missing_config_fails_closed():
    with pytest.raises(RecordPolicyViolation):
        validate_required_metadata({"owner_unit": "TEST"}, {})


@pytest.mark.parametrize("status", ["DECLARED", "ON_HOLD", "DISPOSED"])
def test_declared_or_held_is_immutable(status):
    with pytest.raises(RecordPolicyViolation):
        assert_content_editable(status)


def test_declare_requires_version():
    with pytest.raises(RecordPolicyViolation):
        assert_can_declare("DRAFT", 0)
    assert_can_declare("DRAFT", 1)
