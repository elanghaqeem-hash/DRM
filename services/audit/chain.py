"""Tamper-detecting SHA-256 chain. DBA-resistant WORM is NOT implemented."""
import hashlib
import json
from typing import Any

GENESIS = "0" * 64


def canonical_json(event: dict[str, Any]) -> str:
    return json.dumps(event, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def chain_hash(previous: str, event: dict[str, Any]) -> str:
    if len(previous) != 64 or any(c not in "0123456789abcdef" for c in previous):
        raise ValueError("Invalid preceding SHA-256")
    return hashlib.sha256((previous + "|" + canonical_json(event)).encode()).hexdigest()


def verify_rows(rows: list[dict[str, Any]]) -> tuple[bool, str | None]:
    previous = GENESIS
    last_seq = None
    for row in rows:
        if last_seq is not None and row["seq"] <= last_seq:
            return False, f"Out-of-order audit event at seq {row['seq']}"
        if row["prev_hash"] != previous:
            return False, f"Broken predecessor link at seq {row['seq']}"
        data = {
            "event_id": str(row["event_id"]), "ts": row["ts"].isoformat(),
            "actor_sub": row["actor_sub"], "actor_role": row["actor_role"],
            "source_ip": row["source_ip"], "device": row["device"],
            "action": row["action"], "object_ref": row["object_ref"],
            "before_hash": row["before_hash"], "after_hash": row["after_hash"],
            "result": row["result"],
        }
        if row["payload"] != data:
            return False, f"Audit column/payload mismatch at seq {row['seq']}"
        expected = chain_hash(previous, data)
        if expected != row["event_hash"]:
            return False, f"Hash mismatch at seq {row['seq']}"
        previous = expected
        last_seq = row["seq"]
    return True, None
