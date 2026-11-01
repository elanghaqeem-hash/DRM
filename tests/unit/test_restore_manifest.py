"""Isolated restore manifest verification: no false success on damaged backups."""
from hashlib import sha256

import pytest

from infra.scripts.verify_restore import verify_manifest


def sample_manifest(root):
    items = []
    for component, content in [
        ("database", b"FAKE-PG-DUMP"),
        ("objects", b"SYNTHETIC-OBJECT"),
        ("audit", b"SYNTHETIC-AUDIT"),
    ]:
        name = component + ".bin"
        (root / name).write_bytes(content)
        items.append({
            "path": name, "component": component, "size_bytes": len(content),
            "sha256": sha256(content).hexdigest(),
        })
    return {"version": 1, "files": items}


def test_manifest_verifies_but_is_not_restore_proof(tmp_path):
    result = verify_manifest(tmp_path, sample_manifest(tmp_path))
    assert result["integrity_verified"] is True
    assert result["isolated_restore_verified"] is False
    assert result["files_checked"] == 3


def test_detect_corrupted_blob(tmp_path):
    data = sample_manifest(tmp_path)
    (tmp_path / "objects.bin").write_bytes(b"TAMPERED")
    with pytest.raises(ValueError, match="mismatch"):
        verify_manifest(tmp_path, data)


def test_reject_partial_backup(tmp_path):
    data = sample_manifest(tmp_path)
    data["files"] = data["files"][:2]
    with pytest.raises(ValueError, match="Incomplete backup"):
        verify_manifest(tmp_path, data)


def test_reject_path_traversal(tmp_path):
    data = sample_manifest(tmp_path)
    data["files"][0]["path"] = "../private"
    with pytest.raises(ValueError, match="Unsafe"):
        verify_manifest(tmp_path, data)


def test_reject_symlink(tmp_path):
    data = sample_manifest(tmp_path)
    (tmp_path / "objects.bin").unlink()
    (tmp_path / "objects.bin").symlink_to(tmp_path / "audit.bin")
    with pytest.raises(ValueError, match="unsafe"):
        verify_manifest(tmp_path, data)
