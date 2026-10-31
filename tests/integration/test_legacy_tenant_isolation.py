"""All legacy archive tables are scoped, quarantined, and FK-consistent."""
import os
from uuid import uuid4
import psycopg
import pytest

pytestmark = pytest.mark.integration

LEGACY = (
    "classification_scheme", "retention_rule", "record_class", "aggregation",
    "record", "record_aggregation", "record_version", "physical_location",
    "physical_item", "loan", "legal_hold", "legal_hold_scope",
    "disposition_batch", "disposition_item", "disposition_certificate",
    "access_request", "pdp_processing_register", "data_subject_request",
    "role", "permission", "role_permission", "user_attribute",
    "access_review_campaign", "audit_event",
)


def test_legacy_rls_fks_and_quarantine():
    admin_url = os.environ["DATABASE_URL"]
    runtime_url = os.environ["RUNTIME_DATABASE_URL"]
    tenant_a, tenant_b, scheme_id, record_class_id, record_id = [uuid4() for _ in range(5)]
    with psycopg.connect(admin_url) as admin:
        with admin.transaction():
            admin.execute(
                "INSERT INTO edarms_tenant(id,code,name) VALUES "
                "(%s,%s,'Synthetic A'),(%s,%s,'Synthetic B')",
                (tenant_a, "legacy-" + tenant_a.hex[:12],
                 tenant_b, "legacy-" + tenant_b.hex[:12]),
            )
            admin.execute(
                "INSERT INTO classification_scheme "
                "(id,tenant_id,code,name,version) VALUES (%s,%s,%s,'Synthetic',1)",
                (scheme_id, tenant_a, "class-" + scheme_id.hex[:12]),
            )
            admin.execute(
                "INSERT INTO record_class "
                "(id,tenant_id,scheme_id,code,name,security_default) "
                "VALUES (%s,%s,%s,'SC','Synthetic','INTERNAL')",
                (record_class_id, tenant_a, scheme_id),
            )
            admin.execute(
                "INSERT INTO record "
                "(id,tenant_id,record_no,class_id,title,security_level,owner_unit,created_by) "
                "VALUES (%s,%s,%s,%s,'Synthetic','INTERNAL','Unit A','user-a')",
                (record_id, tenant_a, "REC-" + record_id.hex, record_class_id),
            )
            rows = admin.execute(
                "SELECT relname,relrowsecurity,relforcerowsecurity "
                "FROM pg_class WHERE relname=ANY(%s)",
                (list(LEGACY),),
            ).fetchall()
            assert len(rows) == len(LEGACY)
            assert all(rls and force for _, rls, force in rows)
            # Existing NULL rows stay quarantined, but new inserts cannot lack tenant.
            assert admin.execute(
                "SELECT convalidated FROM pg_constraint "
                "WHERE conname='record_new_tenant_required'"
            ).fetchone()[0] is False
        with pytest.raises(psycopg.errors.CheckViolation):
            admin.execute(
                "INSERT INTO classification_scheme(code,name,version) "
                "VALUES (%s,'No tenant',1)", ("orphan-" + uuid4().hex[:12],)
            )
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            admin.execute(
                "INSERT INTO record_class "
                "(tenant_id,scheme_id,code,name,security_default) "
                "VALUES (%s,%s,'CROSS','Bad','INTERNAL')",
                (tenant_b, scheme_id),
            )

    with psycopg.connect(runtime_url) as connection:
        with connection.transaction():
            role = connection.execute(
                "SELECT rolsuper,rolbypassrls FROM pg_roles "
                "WHERE rolname=current_user"
            ).fetchone()
            assert role == (False, False)
            # No tenant setting => legacy records inaccessible even by direct ID.
            assert connection.execute(
                "SELECT id FROM record WHERE id=%s", (record_id,)
            ).fetchall() == []
            connection.execute(
                "SELECT set_config('edarms.tenant_id',%s,true)", (str(tenant_b),)
            )
            assert connection.execute(
                "SELECT id FROM record WHERE id=%s", (record_id,)
            ).fetchall() == []
            assert connection.execute(
                "SELECT id FROM classification_scheme WHERE id=%s", (scheme_id,)
            ).fetchall() == []
        with connection.transaction():
            connection.execute(
                "SELECT set_config('edarms.tenant_id',%s,true)", (str(tenant_a),)
            )
            assert connection.execute(
                "SELECT id FROM record WHERE id=%s", (record_id,)
            ).fetchone()[0] == record_id
