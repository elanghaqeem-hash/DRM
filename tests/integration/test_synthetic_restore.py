"""Actual PostgreSQL dump→restore rehearsal in a disposable isolated DB.

A successful synthetic DB rehearsal is NOT approval of Bank RPO/RTO, object
store restoration, independent immutable audit anchor or Bank production DR.
"""
import json
import os
from hashlib import sha256
from pathlib import Path
import subprocess
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
import pytest

from infra.scripts.verify_restore import restore_isolated

pytestmark = pytest.mark.integration


def _pg_environment(url: str, dbname: str) -> dict:
    details = conninfo_to_dict(url)
    env = os.environ.copy()
    for name, field in (
        ("PGHOST", "host"), ("PGPORT", "port"), ("PGUSER", "user"),
        ("PGPASSWORD", "password"),
    ):
        if details.get(field):
            env[name] = str(details[field])
    env["PGDATABASE"] = dbname
    return env


def _manifest_file(root: Path, component: str, name: str, payload: bytes) -> dict:
    (root / name).write_bytes(payload)
    return {
        "component": component, "path": name,
        "sha256": sha256(payload).hexdigest(), "size_bytes": len(payload),
    }


def test_real_synthetic_pg_dump_pg_restore_and_reconciliation(tmp_path, monkeypatch):
    source_url = os.environ["DATABASE_URL"]
    source_params = conninfo_to_dict(source_url)
    source_name = source_params.get("dbname") or source_params.get("database")
    assert source_name, "Source DB name required"
    new_name = "edarms_restore_" + uuid4().hex[:12]
    counts = {}
    tables = ("record", "record_version", "legal_hold", "audit_event")
    with psycopg.connect(source_url) as source:
        for table in tables:
            counts[table] = source.execute(
                sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
            ).fetchone()[0]
    with psycopg.connect(source_url, autocommit=True) as source:
        source.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_name)))
    try:
        dump = tmp_path / "database.dump"
        subprocess.run(
            ["pg_dump", "--format=custom", "--no-owner", "--no-acl",
             "--dbname", source_name, "--file", str(dump)],
            env=_pg_environment(source_url, source_name),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True, timeout=180,
        )
        audit_payload = json.dumps(
            {"synthetic_counts": counts, "bank_audit_anchor_verified": False},
            sort_keys=True,
        ).encode("utf-8")
        objects_payload = b"synthetic-object-backup-not-bank-worm"
        manifest = {
            "version": 1,
            "expected_counts": counts,
            "files": [
                {"component": "database", "path": dump.name,
                 "sha256": sha256(dump.read_bytes()).hexdigest(),
                 "size_bytes": dump.stat().st_size},
                _manifest_file(tmp_path, "objects", "objects.backup", objects_payload),
                _manifest_file(tmp_path, "audit", "audit-manifest.json", audit_payload),
            ],
        }
        target_url = make_conninfo(source_url, dbname=new_name)
        for key, value in _pg_environment(source_url, new_name).items():
            if key.startswith("PG"):
                monkeypatch.setenv(key, value)
        outcome = restore_isolated(tmp_path, manifest, target_url)
        assert outcome["integrity_verified"] is True
        assert outcome["isolated_restore_verified"] is True
        assert outcome["counts_verified"] == counts
        assert outcome["bank_dr_release_verified"] is False
        # Restored DB has same archived records, hold and audit row counts.
        with psycopg.connect(target_url) as restored:
            for table, expected in counts.items():
                actual = restored.execute(
                    sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
                ).fetchone()[0]
                assert actual == expected
    finally:
        with psycopg.connect(source_url, autocommit=True) as source:
            source.execute(
                sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(new_name))
            )
