"""Actual PostgreSQL synthetic classification/draft governance and tenant test."""
import os
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb
import pytest
from fastapi import HTTPException

from services.records.drafts import list_approved_classes, create_controlled_draft

pytestmark = pytest.mark.integration


def test_bank_approved_schema_required_for_draft_and_cross_tenant_denial():
    tenant, other, scheme, class_id = (uuid4() for _ in range(4))
    with psycopg.connect(os.environ["DATABASE_URL"]) as admin:
        with admin.transaction():
            admin.execute(
                """INSERT INTO edarms_tenant(id,code,name) VALUES
                   (%s,%s,'Synthetic Draft A'),(%s,%s,'Synthetic Draft B')""",
                (tenant, "draft-" + tenant.hex[:10],
                 other, "draft-" + other.hex[:10]),
            )
            admin.cursor().executemany(
                """INSERT INTO edarms_membership
                   (tenant_id,actor_sub,role_code,enabled)
                   VALUES(%s,%s,%s,true)""",
                [(tenant, "archivist", "records_officer"),
                 (tenant, "readonly", "auditor"),
                 (other, "other-archivist", "records_officer")],
            )
            admin.execute(
                """INSERT INTO classification_scheme
                   (id,tenant_id,code,name,version,approval_status,
                    proposed_by,approved_by)
                   VALUES(%s,%s,%s,'Synthetic Policy',1,
                          'APPROVED','maker','checker')""",
                (scheme, tenant, "DRAFT-SCHEME-" + scheme.hex[:8]),
            )
            admin.execute(
                """INSERT INTO record_class
                   (id,tenant_id,scheme_id,code,name,security_default,required_metadata)
                   VALUES(%s,%s,%s,%s,'Synthetic file plan','INTERNAL',%s)""",
                (class_id, tenant, scheme, "DRAFT-CLASS-" + class_id.hex[:8],
                 Jsonb({"required_fields": ["event_date", "source_unit"]})),
            )

    url = os.environ["RUNTIME_DATABASE_URL"]
    classes = list_approved_classes(url, tenant, "archivist")["items"]
    assert len(classes) == 1
    assert classes[0]["id"] == class_id
    with pytest.raises(HTTPException) as denied_class:
        list_approved_classes(url, other, "archivist")
    assert denied_class.value.status_code == 403
    with pytest.raises(HTTPException) as hidden_class:
        create_controlled_draft(url, other, class_id, "other-archivist",
                                "Synthetic document", "UNIT", {
                                    "event_date": "2026-11-01",
                                    "source_unit": "UNIT",
                                })
    assert hidden_class.value.status_code == 404

    with pytest.raises(HTTPException) as missing_metadata:
        create_controlled_draft(url, tenant, class_id, "archivist",
                                "Synthetic document", "UNIT", {"event_date": "2026-11-01"})
    assert missing_metadata.value.status_code == 422
    with pytest.raises(HTTPException) as role_denied:
        create_controlled_draft(url, tenant, class_id, "readonly",
                                "Synthetic document", "UNIT", {
                                    "event_date": "2026-11-01", "source_unit": "UNIT",
                                })
    assert role_denied.value.status_code == 403

    created = create_controlled_draft(url, tenant, class_id, "archivist",
                                      "Synthetic document", "UNIT", {
                                          "event_date": "2026-11-01",
                                          "source_unit": "UNIT",
                                      })
    assert created["status"] == "DRAFT"
    assert created["record_no"].startswith("DRAFT-")
    assert created["content_declared"] is False
    assert created["original_storage_verified"] is False

    with psycopg.connect(os.environ["DATABASE_URL"]) as admin:
        row = admin.execute(
            """SELECT status,created_by FROM record WHERE id=%s AND tenant_id=%s""",
            (created["id"], tenant),
        ).fetchone()
        assert row == ("DRAFT", "archivist")
        assert admin.execute(
            """SELECT count(*) FROM edarms_draft_event
               WHERE tenant_id=%s AND record_id=%s AND event_type='DRAFT_CREATED'""",
            (tenant, created["id"]),
        ).fetchone()[0] == 1

    # Runtime may not create DECLARED objects or bypass signed actor context.
    with psycopg.connect(url) as limited:
        with limited.transaction():
            limited.execute("SELECT set_config('edarms.tenant_id',%s,true)",
                            (str(tenant),))
            limited.execute("SELECT set_config('edarms.actor_sub',%s,true)",
                            ("archivist",))
            with pytest.raises(psycopg.errors.RaiseException):
                with limited.transaction():
                    limited.execute(
                        """INSERT INTO record
                           (tenant_id,record_no,class_id,title,security_level,
                            owner_unit,created_by,status,metadata)
                           VALUES(%s,%s,%s,'Forgery','INTERNAL','UNIT',
                                  'archivist','DECLARED',%s)""",
                        (tenant, "DRAFT-" + uuid4().hex, class_id,
                         Jsonb({"event_date": "2026-11-01", "source_unit": "UNIT"})),
                    )
