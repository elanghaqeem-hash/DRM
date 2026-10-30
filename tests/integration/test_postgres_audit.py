"""Run only against a disposable migrated PostgreSQL database."""
import os
import pytest
import psycopg
from services.audit.store import append_event, verify_chain

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def url():
    value = os.environ.get("DATABASE_URL")
    if not value:
        pytest.skip("DATABASE_URL required")
    return value


def test_audit_write_and_mutation_denied(url):
    row = append_event(
        url, actor_sub="fictitious-actor", actor_role="audit_writer",
        source_ip="127.0.0.1", device=None, action="CREATE",
        object_ref="CONTOH-TEST-ONLY", before_hash=None, after_hash=None, result="SUCCESS",
    )
    report = verify_chain(url)
    assert report["valid"] and row["event_hash"] == report["head_hash"]
    assert not report["external_anchor_verified"]
    with psycopg.connect(url) as connection:
        with pytest.raises(psycopg.errors.RaiseException):
            connection.execute("UPDATE audit_event SET action='ALTERED' WHERE seq=%s",
                               (row["seq"],))
