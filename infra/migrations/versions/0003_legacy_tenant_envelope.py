"""Deny-by-default tenant envelope for ALL legacy archive tables.

No guessing/backfilling tenant identity: existing NULL rows become quarantined
invisible under RLS. New inserts need an explicit tenant and composite FK
relations prevent linking records from distinct tenants.
"""
from alembic import op

revision = "0003_legacy_tenant_envelope"
down_revision = "0002_tenant_workspace"
branch_labels = None
depends_on = None

LEGACY = (
    "classification_scheme", "retention_rule", "record_class", "aggregation",
    "record", "record_aggregation", "record_version", "physical_location",
    "physical_item", "loan", "legal_hold", "legal_hold_scope",
    "disposition_batch", "disposition_item", "disposition_certificate",
    "access_request", "pdp_processing_register", "data_subject_request",
    "role", "permission", "role_permission", "user_attribute",
    "access_review_campaign", "audit_event",
)

# (child, fk column, parent) — ADD NOT VALID is intentional: historical records
# are quarantined until Bank provenance has been independently reconciled.
RELATIONS = (
    ("record_class", "scheme_id", "classification_scheme"),
    ("record_class", "parent_id", "record_class"),
    ("record_class", "retention_rule_id", "retention_rule"),
    ("aggregation", "parent_id", "aggregation"),
    ("record", "class_id", "record_class"),
    ("record_aggregation", "record_id", "record"),
    ("record_aggregation", "aggregation_id", "aggregation"),
    ("record_version", "record_id", "record"),
    ("physical_location", "parent_id", "physical_location"),
    ("physical_item", "record_id", "record"),
    ("physical_item", "location_id", "physical_location"),
    ("loan", "record_id", "record"),
    ("legal_hold_scope", "hold_id", "legal_hold"),
    ("legal_hold_scope", "record_id", "record"),
    ("disposition_item", "batch_id", "disposition_batch"),
    ("disposition_item", "record_id", "record"),
    ("disposition_certificate", "batch_id", "disposition_batch"),
    ("access_request", "record_id", "record"),
    ("pdp_processing_register", "class_id", "record_class"),
    ("role_permission", "role_id", "role"),
    ("role_permission", "permission_id", "permission"),
)


def upgrade():
    op.execute("""
DO $$
BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'edarms_runtime') THEN
   CREATE ROLE edarms_runtime NOLOGIN NOSUPERUSER NOBYPASSRLS;
 END IF;
END $$;
    """)
    # Membership itself must not become an unscoped cross-tenant table.
    for table in ("edarms_tenant", "edarms_membership"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        scope = "id" if table == "edarms_tenant" else "tenant_id"
        op.execute(
            f"CREATE POLICY {table}_scope ON {table} "
            f"USING ({scope} = nullif(current_setting('edarms.tenant_id', true), '')::uuid) "
            f"WITH CHECK ({scope} = nullif(current_setting('edarms.tenant_id', true), '')::uuid)"
        )

    for table in LEGACY:
        op.execute(
            f"ALTER TABLE {table} ADD COLUMN tenant_id uuid "
            "REFERENCES edarms_tenant(id)"
        )
        # NOT VALID lets existing, unclassified records remain quarantined.
        # It DOES reject all new writes with NULL tenant_id.
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {table}_new_tenant_required "
            "CHECK (tenant_id IS NOT NULL) NOT VALID"
        )
        op.execute(f"CREATE INDEX ix_{table}_tenant ON {table}(tenant_id)")
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_scope ON {table} "
            "USING (tenant_id = nullif(current_setting('edarms.tenant_id', true), '')::uuid) "
            "WITH CHECK (tenant_id = nullif(current_setting('edarms.tenant_id', true), '')::uuid)"
        )

    # RLS by itself cannot prevent a TENANT A row with a TENANT B FK; these
    # constraints protect writes and are validated after approved backfill.
    parents = {parent for _, _, parent in RELATIONS}
    for table in sorted(parents):
        op.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT uq_{table}_tenant_id "
            "UNIQUE (tenant_id,id)"
        )
    for child, fk, parent in RELATIONS:
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{child}_{fk}_tenant "
            f"FOREIGN KEY (tenant_id,{fk}) REFERENCES {parent}(tenant_id,id) NOT VALID"
        )

    op.execute(
        "ALTER TABLE edarms_review_task "
        "ADD CONSTRAINT uq_edarms_review_task_tenant_id UNIQUE(tenant_id,id)"
    )
    op.execute(
        "ALTER TABLE edarms_task_event ADD CONSTRAINT fk_event_task_tenant "
        "FOREIGN KEY(tenant_id,task_id) "
        "REFERENCES edarms_review_task(tenant_id,id) NOT VALID"
    )
    op.execute("GRANT USAGE ON SCHEMA public TO edarms_runtime")
    op.execute("GRANT SELECT ON edarms_tenant, edarms_membership TO edarms_runtime")
    op.execute(
        "GRANT SELECT,INSERT,UPDATE ON edarms_review_task TO edarms_runtime"
    )
    op.execute("GRANT SELECT,INSERT ON edarms_task_event TO edarms_runtime")
    op.execute("GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO edarms_runtime")
    # Legacy records remain deliberately read-only to the app until business
    # controls are implemented; RLS denies unmapped historical records.
    op.execute(f"GRANT SELECT ON {', '.join(LEGACY)} TO edarms_runtime")
    op.execute("GRANT INSERT ON audit_event TO edarms_runtime")


def downgrade():
    raise RuntimeError("Tenant quarantine and immutable evidence must not be removed automatically")
