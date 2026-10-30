"""Verify all legacy record tables are tenant scoped; synthetic PostgreSQL fixture."""
from uuid import uuid4

import psycopg
import pytest


@pytest.mark.integration
def test_archive_tables_enforce_rls_cross_tenant_keys_and_immutability():
    import os
    url = os.environ["DATABASE_URL"]
    a, b = uuid4(), uuid4()
    scheme = uuid4()
    other_scheme = uuid4()
    cls = uuid4()
    other_cls = uuid4()
    record = uuid4()
    version = uuid4()
    with psycopg.connect(url) as conn:
        with conn.transaction():
            conn.execute(
                "INSERT INTO edarms_tenant(id,code,name) VALUES (%s,%s,%s),(%s,%s,%s)",
                (a, "iso-" + a.hex[:12], "Synthetic Isolation A",
                 b, "iso-" + b.hex[:12], "Synthetic Isolation B"),
            )
            conn.execute(
                """INSERT INTO classification_scheme
                   (id,tenant_id,code,name,version)
                   VALUES (%s,%s,'TAX','Taxonomy',1),(%s,%s,'TAX','Taxonomy',1)""",
                (scheme, a, other_scheme, b),
            )
            conn.execute(
                """INSERT INTO record_class
                   (id,tenant_id,scheme_id,code,name,security_default)
                   VALUES (%s,%s,%s,'A','Test','INTERNAL'),
                          (%s,%s,%s,'B','Test','INTERNAL')""",
                (cls, a, scheme, other_cls, b, other_scheme),
            )
            conn.execute(
                """INSERT INTO record
                   (id,tenant_id,record_no,class_id,title,security_level,owner_unit,created_by)
                   VALUES (%s,%s,'REC-001',%s,'Synthetic','INTERNAL','TEST','creator')""",
                (record, a, cls),
            )
            conn.execute(
                """INSERT INTO record_version
                   (id,tenant_id,record_id,major_version,object_key,mime,size_bytes,
                    sha256,created_by)
                   VALUES (%s,%s,%s,1,'test/immutable-001','application/pdf',3,%s,'creator')""",
                (version, a, record, "a" * 64),
            )
    with psycopg.connect(url) as conn:
        with conn.transaction():
            # Existing CI bootstrap role owns the tables and is superuser.
            # Test RLS only while running as non-BYPASSRLS role.
            conn.execute("SET LOCAL ROLE pg_read_all_data")
            assert conn.execute(
                "SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user"
            ).fetchone()[0] is False
            conn.execute("SELECT set_config('edarms.tenant_id',%s,true)", (str(b),))
            assert conn.execute(
                "SELECT id FROM record WHERE id=%s", (record,)
            ).fetchall() == []
            assert conn.execute(
                "SELECT id FROM record_version WHERE id=%s", (version,)
            ).fetchall() == []
            assert conn.execute("SELECT count(*) FROM classification_scheme").fetchone()[0] == 1
        with conn.transaction():
            conn.execute("SET LOCAL ROLE pg_read_all_data")
            # No tenant set: default-deny, including search counts.
            assert conn.execute("SELECT count(*) FROM record").fetchone()[0] == 0
        with conn.transaction():
            with pytest.raises(psycopg.errors.ForeignKeyViolation):
                # Even a superuser cannot attach A's record to a version for B.
                with conn.transaction():
                    conn.execute(
                        """INSERT INTO record_version
                        (tenant_id,record_id,major_version,object_key,mime,size_bytes,
                         sha256,created_by)
                        VALUES (%s,%s,2,'test/attack','application/pdf',3,%s,'creator')""",
                        (b, record, "b" * 64),
                    )
        with conn.transaction():
            with pytest.raises(psycopg.errors.RaiseException):
                with conn.transaction():
                    conn.execute(
                        "UPDATE record_version SET sha256=%s WHERE id=%s",
                        ("b" * 64, version),
                    )
        with conn.transaction():
            conn.execute("UPDATE record SET status='DECLARED' WHERE id=%s", (record,))
        with conn.transaction():
            with pytest.raises(psycopg.errors.RaiseException):
                with conn.transaction():
                    conn.execute(
                        "UPDATE record SET title='tampered' WHERE id=%s", (record,)
                    )
        with conn.transaction():
            with pytest.raises(psycopg.errors.RaiseException):
                with conn.transaction():
                    conn.execute("DELETE FROM record WHERE id=%s", (record,))

