"""Pure SHA-256 audit chain tests with fictitious examples."""
from datetime import datetime, timezone
from uuid import uuid4
import pytest
from services.audit.chain import GENESIS, canonical_json, chain_hash, verify_rows


def sample_rows():
    previous, rows = GENESIS, []
    for i in range(3):
        payload = {
            "event_id": str(uuid4()), "ts": datetime(2026, 10, 30, 4, i, tzinfo=timezone.utc),
            "actor_sub": "test-actor", "actor_role": "auditor", "source_ip": "127.0.0.1",
            "device": None, "action": "READ", "object_ref": f"CONTOH-{i}",
            "before_hash": None, "after_hash": None, "result": "SUCCESS",
        }
        digest = chain_hash(previous, {**payload, "ts": payload["ts"].isoformat()})
        rows.append({"seq": i + 1, **payload, "prev_hash": previous,
                     "event_hash": digest,
                     "payload": {**payload, "ts": payload["ts"].isoformat()}})
        previous = digest
    return rows


def test_stable_canonical_order():
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_hash_sensitive_to_input():
    assert chain_hash(GENESIS, {"a": 1}) != chain_hash(GENESIS, {"a": 2})


def test_invalid_predecessor():
    with pytest.raises(ValueError):
        chain_hash("oops", {"a": 1})


def test_valid_chain():
    assert verify_rows(sample_rows()) == (True, None)


def test_column_mutation():
    rows = sample_rows()
    rows[1]["action"] = "DOWNLOAD"
    assert "mismatch" in verify_rows(rows)[1].lower()


def test_payload_and_column_mutation():
    rows = sample_rows()
    rows[1]["action"] = "DOWNLOAD"
    rows[1]["payload"]["action"] = "DOWNLOAD"
    assert "hash mismatch" in verify_rows(rows)[1].lower()


def test_predecessor_mutation():
    rows = sample_rows()
    rows[1]["prev_hash"] = GENESIS
    assert "predecessor" in verify_rows(rows)[1].lower()
