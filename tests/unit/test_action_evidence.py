"""Prevent a designed button or unaudited test from being called Bank-PASS."""
import csv
from pathlib import Path

import pytest

from infra.scripts.action_evidence import coverage


def test_real_action_registry_reports_no_bank_uat():
    report = coverage(Path("docs/UX/action-registry.csv"))
    assert report["registered_actions"] == 414
    assert report["registered_submenus"] == 62
    assert report["verified_bank_uat"] == 0
    assert report["production_coverage_complete"] is False


def test_forged_verified_marker_without_independent_evidence_is_rejected(tmp_path):
    registry = tmp_path / "registry.csv"
    with registry.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=[
            "action_id", "submenu", "status", "api_contract", "permission"
        ])
        writer.writeheader()
        writer.writerow({
            "action_id": "F4-01", "submenu": "F4",
            "status": "VERIFIED_BANK_UAT", "api_contract": "TBD",
            "permission": "TBD-BANK/deny by default",
        })
    with pytest.raises(ValueError, match="Unsubstantiated"):
        coverage(registry)
