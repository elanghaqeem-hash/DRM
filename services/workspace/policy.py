"""Pure, Bank-neutral authorization and maker-checker rules for PoC review tasks.

These tasks do not grant permission to declare, transfer or destroy a record.
"""
from dataclasses import dataclass


class WorkspacePolicyError(ValueError):
    """A workspace action is forbidden or conflicts with an immutable decision."""


CREATE_ROLES = frozenset({"records_officer", "records_manager"})
DECIDE_ROLES = frozenset({"approver", "records_manager"})


@dataclass(frozen=True)
class ReviewTask:
    status: str
    version: int
    created_by: str
    assigned_to: str


def require_scoped_role(enabled_roles: set[str], permitted: frozenset[str]) -> None:
    if not enabled_roles.intersection(permitted):
        raise WorkspacePolicyError("No active tenant-scoped permission")


def check_decision(task: ReviewTask, actor_sub: str, expected_version: int) -> None:
    if not actor_sub or task.created_by == actor_sub:
        raise WorkspacePolicyError("Maker cannot approve or reject own task")
    if task.assigned_to != actor_sub:
        raise WorkspacePolicyError("Only assigned checker may decide")
    if task.status != "OPEN":
        raise WorkspacePolicyError("Task is already decided")
    if task.version != expected_version:
        raise WorkspacePolicyError("Stale task version")
