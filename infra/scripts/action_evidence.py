"""Machine-readable action evidence ledger; no manufactured Bank PASS values.

Default mode reports implementation gaps. Explicit --production-gate requires
all 414 actions to have independent Bank-UAT evidence; synthetic CI must not
pretend that a registry entry is a working button.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

DEFAULT_REGISTRY = Path("docs/UX/action-registry.csv")
DEFAULT_EVIDENCE = Path("docs/UAT/executed-evidence.json")


def coverage(registry: Path, evidence: Path | None = None) -> dict:
    with registry.open(encoding="utf-8", newline="") as fp:
        rows = list(csv.DictReader(fp))
    ids = [row["action_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate action IDs")
    submenus = {row["submenu"] for row in rows}
    statuses = Counter(row["status"] for row in rows)
    uat = {}
    if evidence is not None and evidence.exists():
        uat = json.loads(evidence.read_text(encoding="utf-8"))
    if not isinstance(uat, dict):
        raise ValueError("UAT evidence must be a dictionary")
    verified = 0
    unsupported = []
    for row in rows:
        action_id = row["action_id"]
        if row["status"] != "VERIFIED_BANK_UAT":
            continue
        proof = uat.get(action_id, {})
        required = (
            "test_reference", "execution_commit", "browser_e2e_ref",
            "bank_uat_signoff", "bank_approver",
        )
        if (not isinstance(proof, dict) or any(not proof.get(k) for k in required)
                or row["api_contract"] == "TBD"
                or row["permission"].startswith("TBD-BANK")):
            unsupported.append(action_id)
        else:
            verified += 1
    if unsupported:
        raise ValueError("Unsubstantiated VERIFIED_BANK_UAT: " + ", ".join(unsupported))
    return {
        "registered_actions": len(rows),
        "registered_submenus": len(submenus),
        "verified_bank_uat": verified,
        "not_bank_uat_verified": len(rows) - verified,
        "status_counts": dict(statuses),
        "production_coverage_complete": len(rows) == 414
        and len(submenus) == 62 and verified == 414,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--production-gate", action="store_true")
    args = parser.parse_args()
    report = coverage(args.registry, args.evidence)
    print(json.dumps(report, sort_keys=True))
    if args.production_gate and not report["production_coverage_complete"]:
        parser.exit(2, "EDARMS release denied: 62/414 Bank UAT evidence incomplete\n")


if __name__ == "__main__":
    main()
