"""Fail-closed tenant retrofit of EMPTY legacy archive tables.

No data migration, no implicit tenant mapping. Existing Bank data requires
separate, signed inventory/backfill and reconciliation before this migration.
"""
from alembic import op

revision = "0003_archive_tenant_isolation"
down_revision = "0002_tenant_workspace"
branch_labels = None
depends_on = None

ARCHIVE_TABLES = (
    "classification_scheme", "retention_rule", "record_class", "aggregation",
    "record", "record_aggregation", "record_version", "physical_location",
    "physical_item", "loan", "legal_hold", "legal_hold_scope",
    "disposition_batch", "disposition_item", "disposition_certificate",
    "access_request", "pdp_processing_register", "data_subject_request",
)

# Fixed identifiers only; never build identifiers from user-supplied values.
LINKS = (
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
)


def upgrade():
    bind = op.get_bind()
    # Inventory in one transaction; any nonempty table blocks schema change.
    # This prevents silently reassigning legacy documents to a fabricated Bank.
    nonempty = [
        table for table in ARCHIVE_TABLES
        if bind.exec_driver_sql(f"SELECT EXISTS (SELECT 1 FROM {table})").scalar()
    ]
    if nonempty:
        raise RuntimeError(
            "Tenant backfill and signed reconciliation required; tables not empty: "
            + ", ".join(nonempty)
        )

    for table in ARCHIVE_TABLES:
        op.execute(
            f"ALTER TABLE {table} ADD COLUMN tenant_id uuid NOT NULL "
            "REFERENCES edarms_tenant(id)"
        )
        if table != "record_aggregation":
            op.execute(f"ALTER TABLE {table} ADD CONSTRAINT uq_{table}_tenant_id "
                       "UNIQUE (tenant_id,id)")
        op.execute(f"CREATE INDEX ix_{table}_tenant ON {table}(tenant_id)")
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_tenant_scope ON {table} "
            "USING (tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid) "
            "WITH CHECK (tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid)"
        )

    # Composite tenant FKs prevent a record in Bank A from referencing Bank B
    # even when written by a migration/operator with BYPASSRLS privileges.
    op.execute("ALTER TABLE record_aggregation ADD CONSTRAINT "
               "uq_record_aggregation_tenant_record UNIQUE (tenant_id,record_id,aggregation_id)")
    for child, column, parent in LINKS:
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{child}_{column}_tenant "
            f"FOREIGN KEY (tenant_id,{column}) REFERENCES {parent}(tenant_id,id)"
        )

    # Bank-scoped numbers: cross-bank duplicate identifiers must not leak.
    op.execute("ALTER TABLE record DROP CONSTRAINT record_record_no_key")
    op.execute("ALTER TABLE record ADD CONSTRAINT uq_record_tenant_no "
               "UNIQUE (tenant_id,record_no)")
    op.execute("ALTER TABLE classification_scheme "
               "DROP CONSTRAINT classification_scheme_code_version_key")
    op.execute("ALTER TABLE classification_scheme ADD CONSTRAINT uq_scheme_tenant_code_version "
               "UNIQUE (tenant_id,code,version)")
    op.execute("ALTER TABLE retention_rule DROP CONSTRAINT retention_rule_code_version_key")
    op.execute("ALTER TABLE retention_rule ADD CONSTRAINT uq_rule_tenant_code_version "
               "UNIQUE (tenant_id,code,version)")

    # Bank Legal roles are provisioned only by controlled IAM/onboarding.
    op.execute("""
ALTER TABLE edarms_membership DROP CONSTRAINT edarms_membership_role_code_check;
ALTER TABLE edarms_membership ADD CONSTRAINT edarms_membership_role_code_check
 CHECK(role_code IN ('records_officer','records_manager','approver','auditor',
                     'legal_officer','compliance_officer'));
ALTER TABLE edarms_membership ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_membership FORCE ROW LEVEL SECURITY;
CREATE POLICY edarms_membership_tenant ON edarms_membership
 USING(tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK(tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid);
ALTER TABLE edarms_tenant ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_tenant FORCE ROW LEVEL SECURITY;
CREATE POLICY edarms_tenant_scope ON edarms_tenant
 USING(id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK(id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid);
ALTER TABLE legal_hold ADD CONSTRAINT uq_legal_hold_tenant_case
 UNIQUE (tenant_id,case_ref);
ALTER TABLE legal_hold ADD CONSTRAINT ck_hold_independent_release
 CHECK (status <> 'RELEASED' OR (approved_by IS NOT NULL
  AND approved_by <> owner_sub AND released_at IS NOT NULL));
    """)

    # Fail closed until independent legally authorized destruction is built.
    op.execute("""
ALTER TABLE record ADD CONSTRAINT ck_record_no_unapproved_disposal
 CHECK(status <> 'DISPOSED');
ALTER TABLE disposition_batch ADD CONSTRAINT ck_batch_no_unapproved_execution
 CHECK(status <> 'EXECUTED');
    """)

    # The actual object bytes are stored elsewhere. Record versions carry
    # immutable checksum references; changing a row is not a valid correction.
    op.execute("""
CREATE OR REPLACE FUNCTION edarms_reject_version_mutation() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'Immutable record version: create a linked new version instead';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_record_version_immutable
BEFORE UPDATE OR DELETE ON record_version
FOR EACH ROW EXECUTE FUNCTION edarms_reject_version_mutation();

CREATE OR REPLACE FUNCTION edarms_protect_record() RETURNS trigger AS $$
BEGIN
 IF TG_OP = 'DELETE' THEN
  RAISE EXCEPTION 'Record deletion requires a separately approved disposal engine';
 END IF;
 IF NEW.tenant_id IS DISTINCT FROM OLD.tenant_id THEN
  RAISE EXCEPTION 'Record tenant cannot be changed';
 END IF;
 IF OLD.status <> 'DRAFT' AND (
  NEW.title IS DISTINCT FROM OLD.title
  OR NEW.metadata IS DISTINCT FROM OLD.metadata
  OR NEW.class_id IS DISTINCT FROM OLD.class_id
  OR NEW.record_no IS DISTINCT FROM OLD.record_no
  OR NEW.created_by IS DISTINCT FROM OLD.created_by
  OR NEW.tenant_id IS DISTINCT FROM OLD.tenant_id
  OR NEW.security_level IS DISTINCT FROM OLD.security_level
 ) THEN
  RAISE EXCEPTION 'Declared record content or provenance cannot be rewritten';
 END IF;
 RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_record_protect
BEFORE UPDATE OR DELETE ON record
FOR EACH ROW EXECUTE FUNCTION edarms_protect_record();

CREATE TABLE edarms_archive_control_event (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 record_id uuid NOT NULL,
 actor_sub text NOT NULL,
 event_type text NOT NULL CHECK (event_type IN
  ('RETENTION_PREVIEW','HOLD_CHECK','ACCESS_DENIED','INTEGRITY_ALERT')),
 details jsonb NOT NULL DEFAULT '{}'::jsonb,
 occurred_at timestamptz NOT NULL DEFAULT now(),
 CONSTRAINT fk_archive_event_record_tenant FOREIGN KEY(tenant_id,record_id)
 REFERENCES record(tenant_id,id)
);
ALTER TABLE edarms_archive_control_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_archive_control_event FORCE ROW LEVEL SECURITY;
CREATE POLICY archive_control_event_tenant ON edarms_archive_control_event
 USING (tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid);
CREATE TRIGGER trg_archive_control_event_immutable
BEFORE UPDATE OR DELETE ON edarms_archive_control_event
FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();
CREATE TABLE edarms_legal_hold_event (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 hold_id uuid NOT NULL,
 actor_sub text NOT NULL,
 action text NOT NULL CHECK(action IN ('APPLIED','RELEASED')),
 reason text NOT NULL,
 occurred_at timestamptz NOT NULL DEFAULT now(),
 CONSTRAINT fk_edarms_hold_event_tenant FOREIGN KEY (tenant_id,hold_id)
 REFERENCES legal_hold(tenant_id,id)
);
ALTER TABLE edarms_legal_hold_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_legal_hold_event FORCE ROW LEVEL SECURITY;
CREATE POLICY edarms_hold_event_scope ON edarms_legal_hold_event
 USING(tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK(tenant_id = NULLIF(current_setting('edarms.tenant_id',true),'')::uuid);
CREATE TRIGGER trg_edarms_legal_hold_event_immutable
BEFORE UPDATE OR DELETE ON edarms_legal_hold_event
FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();
    """)


def downgrade():
    raise RuntimeError(
        "Tenant isolation, provenance and record immutability must not be downgraded automatically"
    )
