"""No external Bank fixture: pure negative/positive workspace gates."""
import pytest
from services.workspace.policy import (
    CREATE_ROLES, DECIDE_ROLES, ReviewTask, WorkspacePolicyError,
    check_decision, require_scoped_role,
)


def test_create_only_scoped_roles():
    require_scoped_role({"records_officer"}, CREATE_ROLES)
    with pytest.raises(WorkspacePolicyError):
        require_scoped_role({"auditor"}, CREATE_ROLES)


def test_decide_only_scoped_roles():
    require_scoped_role({"approver"}, DECIDE_ROLES)
    with pytest.raises(WorkspacePolicyError):
        require_scoped_role(set(), DECIDE_ROLES)


def test_self_approval_rejected():
    task = ReviewTask("OPEN", 1, "maker", "maker")
    with pytest.raises(WorkspacePolicyError, match="Maker"):
        check_decision(task, "maker", 1)


def test_other_checker_denied():
    task = ReviewTask("OPEN", 1, "maker", "checker")
    with pytest.raises(WorkspacePolicyError, match="assigned"):
        check_decision(task, "stranger", 1)


def test_stale_version_rejected():
    task = ReviewTask("OPEN", 2, "maker", "checker")
    with pytest.raises(WorkspacePolicyError, match="Stale"):
        check_decision(task, "checker", 1)


def test_decided_task_rejected():
    task = ReviewTask("REJECTED", 2, "maker", "checker")
    with pytest.raises(WorkspacePolicyError, match="already"):
        check_decision(task, "checker", 2)


def test_independent_checker_allowed():
    check_decision(ReviewTask("OPEN", 1, "maker", "checker"), "checker", 1)
