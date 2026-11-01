"""WP02 controlled archival draft capture; no unscanned original declaration."""
from alembic import op

revision = "0005_controlled_drafts"
down_revision = "0004_governed_records"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE edarms_draft_event (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 record_id uuid NOT NULL,
 actor_sub text NOT NULL,
 event_type text NOT NULL CHECK(event_type IN ('DRAFT_CREATED')),
 metadata_sha256 char(64) NOT NULL CHECK(metadata_sha256 ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(tenant_id,record_id) REFERENCES record(tenant_id,id)
);
ALTER TABLE edarms_draft_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_draft_event FORCE ROW LEVEL SECURITY;
CREATE POLICY edarms_draft_event_tenant ON edarms_draft_event
 USING (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid);
CREATE TRIGGER trg_draft_event_immutable
 BEFORE UPDATE OR DELETE ON edarms_draft_event
 FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();

-- The runtime DB identity may create drafts but cannot insert record_version,
-- approve classification, upload originals, declare or execute disposal.
CREATE OR REPLACE FUNCTION edarms_validate_draft_insert() RETURNS trigger AS $$
DECLARE is_privileged boolean;
        required jsonb;
        scheme_approval text;
        default_security text;
        key text;
BEGIN
 SELECT rolsuper OR rolbypassrls INTO is_privileged
 FROM pg_roles WHERE rolname=current_user;
 IF is_privileged THEN
   RETURN NEW;  -- Explicit owner-only synthetic fixture/migration path.
 END IF;
 IF NEW.status <> 'DRAFT'
   OR NEW.created_by IS DISTINCT FROM nullif(
      current_setting('edarms.actor_sub',true),'')
   OR NEW.tenant_id IS DISTINCT FROM nullif(
      current_setting('edarms.tenant_id',true),'')::uuid THEN
    RAISE EXCEPTION 'Runtime may only create authenticated tenant drafts';
 END IF;
 IF NEW.record_no NOT LIKE 'DRAFT-%' THEN
    RAISE EXCEPTION 'Official record numbering requires Bank policy';
 END IF;
 SELECT c.required_metadata, s.approval_status, c.security_default
   INTO required,scheme_approval,default_security
 FROM record_class c JOIN classification_scheme s
  ON s.tenant_id=c.tenant_id AND s.id=c.scheme_id
 WHERE c.tenant_id=NEW.tenant_id AND c.id=NEW.class_id;
 IF scheme_approval IS DISTINCT FROM 'APPROVED'
   OR required IS NULL OR jsonb_typeof(required->'required_fields') <> 'array'
   OR jsonb_array_length(required->'required_fields') = 0
   OR default_security IS DISTINCT FROM NEW.security_level THEN
   RAISE EXCEPTION 'Approved classification and mandatory metadata required';
 END IF;
 FOR key IN SELECT jsonb_array_elements_text(required->'required_fields') LOOP
    IF key IS NULL OR key = '' OR NOT (NEW.metadata ? key)
      OR NEW.metadata->key = 'null'::jsonb
      OR (jsonb_typeof(NEW.metadata->key)='string'
          AND btrim(NEW.metadata->>key)='') THEN
      RAISE EXCEPTION 'Required archival metadata missing';
    END IF;
 END LOOP;
 RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_validate_draft
 BEFORE INSERT ON record
 FOR EACH ROW EXECUTE FUNCTION edarms_validate_draft_insert();

GRANT INSERT ON record TO edarms_runtime;
GRANT SELECT,INSERT ON edarms_draft_event TO edarms_runtime;
GRANT USAGE ON SEQUENCE edarms_draft_event_id_seq TO edarms_runtime;
    """)


def downgrade():
    raise RuntimeError("No automatic removal of archival draft provenance")
