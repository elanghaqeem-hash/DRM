"""Isolated backup/restore verification; NEVER run against Bank production DB.

A trusted manifest references database custom-format dump, audit export and
archived object files. No fake restore success without pg_restore and DB checks.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

import psycopg


REQUIRED_COMPONENTS = frozenset({"database", "objects", "audit"})


def verify_manifest(root: Path, manifest: dict) -> dict:
    if manifest.get("version") != 1:
        raise ValueError("Unsupported backup manifest version")
    items = manifest.get("files")
    if not isinstance(items, list) or not items:
        raise ValueError("Missing manifest files")
    groups = set()
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Invalid manifest entry")
        name = item.get("path")
        component = item.get("component")
        digest = item.get("sha256")
        size = item.get("size_bytes")
        if (not isinstance(name, str) or not name
                or Path(name).is_absolute() or ".." in Path(name).parts
                or name in seen):
            raise ValueError("Unsafe, missing or repeated manifest path")
        if component not in REQUIRED_COMPONENTS:
            raise ValueError("Unknown backup component")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("Invalid SHA-256 manifest digest")
        if not isinstance(size, int) or size < 0:
            raise ValueError("Invalid manifest byte count")
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(
            root.resolve()
        ):
            raise ValueError("Missing or unsafe backup file")
        h = sha256()
        actual_size = 0
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                actual_size += len(chunk)
                h.update(chunk)
        if actual_size != size or h.hexdigest() != digest:
            raise ValueError("Backup file size or SHA-256 mismatch")
        seen.add(name)
        groups.add(component)
    if groups != REQUIRED_COMPONENTS:
        raise ValueError("Incomplete backup: database, objects and audit all required")
    return {"integrity_verified": True, "files_checked": len(items),
            "components": sorted(groups), "isolated_restore_verified": False}


def restore_isolated(root: Path, manifest: dict, database_url: str) -> dict:
    """Destructive to a dedicated disposable restore DB only, never production."""
    report = verify_manifest(root, manifest)
    database_files = [entry for entry in manifest["files"]
                      if entry["component"] == "database"]
    if len(database_files) != 1:
        raise ValueError("Exactly one database custom dump required")
    with psycopg.connect(database_url, connect_timeout=5) as conn:
        db_name = conn.execute("SELECT current_database()").fetchone()[0]
        if not db_name.startswith("edarms_restore_"):
            raise ValueError("Refusing restore target outside isolated database prefix")
        if conn.execute(
            """SELECT count(*) FROM pg_catalog.pg_tables
               WHERE schemaname='public' AND tablename NOT LIKE 'alembic%'"""
        ).fetchone()[0]:
            raise ValueError("Restore target must be a disposable empty database")
    path = root / database_files[0]["path"]
    env = os.environ.copy()
    # Never pass a URL containing password on command line.
    # DATABASE_URL is instead consumed via PostgreSQL standard env vars only.
    if "PGHOST" not in env or "PGUSER" not in env or "PGDATABASE" not in env:
        raise ValueError("PGHOST, PGUSER and PGDATABASE must be configured")
    if env["PGDATABASE"] != db_name:
        raise ValueError("PGDATABASE differs from verified restore target")
    process = subprocess.run(
        ["pg_restore", "--no-owner", "--no-acl", "--exit-on-error",
         "--single-transaction", "--dbname", db_name, str(path)],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=600,
    )
    if process.returncode:
        raise RuntimeError("Isolated pg_restore failed (see private DR logs)")
    expected = manifest.get("expected_counts", {})
    allowed = {"record", "record_version", "legal_hold", "audit_event"}
    if not isinstance(expected, dict) or set(expected) != allowed:
        raise ValueError("Complete expected_counts required for reconciliation")
    actual = {}
    with psycopg.connect(database_url, connect_timeout=5) as conn:
        for name in sorted(allowed):
            actual[name] = conn.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
    if actual != expected:
        raise ValueError("Isolated restore row-count reconciliation failed")
    report["isolated_restore_verified"] = True
    report["counts_verified"] = actual
    # Independent immutable audit anchor and recovered object STORE still require
    # separate signed checks: do not claim full Bank DR from this local procedure.
    report["bank_dr_release_verified"] = False
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--execute-isolated", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = verify_manifest(args.backup_root, manifest)
    if args.execute_isolated:
        if os.getenv("ALLOW_ISOLATED_RESTORE") != "true":
            raise RuntimeError("Explicit isolated restore authorization absent")
        target = os.environ.get("RESTORE_DATABASE_URL")
        if not target:
            raise RuntimeError("RESTORE_DATABASE_URL is required")
        result = restore_isolated(args.backup_root, manifest, target)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
