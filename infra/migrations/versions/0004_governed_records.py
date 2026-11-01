"""WP04 fail-closed, tenant-scoped legal hold and disposition review.

No public Bank JRA approvals, destruction authorization, blob deletion or
unverified legacy-tenant assignment are introduced by this migration.
"""
from alembic import op

revision = "0004_governed_records"
down_revision = "0003_legacy_tenant_envelope"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
ALTER TABLE edarms_membership DROP CONSTRAINT edarms_membership_role_code_check;
ALTER TABLE edarms_membership ADD CONSTRAINT edarms_membership_role_code_check
 CHECK(role_code IN ('records_officer','records_manager','approver','auditor',
                    'legal_officer','compliance_officer'));

-- Bank-controlled policy evidence: NO INSERT/UPDATE grant for application role.
-- Bank officers must validate identity, signature, dates and provenance out of band.
CREATE TABLE edarms_jra_evidence (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 rule_id uuid NOT NULL,
 signed_approval_reference text NOT NULL CHECK(length(trim(signed_approval_reference)) > 5),
 approval_document_sha256 char(64) NOT NULL
    CHECK(approval_document_sha256 ~ '^[0-9a-f]{64}$'),
 signatory_subject text NOT NULL CHECK(length(trim(signatory_subject)) > 1),
 verified_by text NOT NULL CHECK(length(trim(verified_by)) > 1),
 effective_from date NOT NULL,
 effective_until date,
 registered_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY (tenant_id,rule_id) REFERENCES retention_rule(tenant_id,id),
 UNIQUE(tenant_id,rule_id),
 CHECK(signatory_subject <> verified_by),
 CHECK(effective_until IS NULL OR effective_until >= effective_from)
);

CREATE TABLE edarms_hold_event (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 hold_id uuid NOT NULL,
 record_id uuid NOT NULL,
 actor_sub text NOT NULL,
 action text NOT NULL CHECK(action IN ('APPLIED','RELEASED')),
 reason text NOT NULL CHECK(length(trim(reason)) >= 4),
 created_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(tenant_id,hold_id) REFERENCES legal_hold(tenant_id,id),
 FOREIGN KEY(tenant_id,record_id) REFERENCES record(tenant_id,id)
);
CREATE INDEX ix_edarms_hold_event_record ON edarms_hold_event(tenant_id,record_id);

CREATE TABLE edarms_disposition_case (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 record_id uuid NOT NULL,
 status text NOT NULL DEFAULT 'PROPOSED'
     CHECK(status IN ('PROPOSED','REVIEWED','APPROVED','REJECTED')),
 version integer NOT NULL DEFAULT 1 CHECK(version > 0),
 proposed_by text NOT NULL,
 proposed_reason text NOT NULL CHECK(length(trim(proposed_reason)) >= 8),
 reviewed_by text,
 reviewed_at timestamptz,
 approved_by text,
 approved_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(tenant_id,record_id) REFERENCES record(tenant_id,id),
 UNIQUE(tenant_id,id),
 CHECK(reviewed_by IS NULL OR reviewed_by <> proposed_by),
 CHECK(approved_by IS NULL OR
      (approved_by <> proposed_by AND approved_by <> reviewed_by)),
 CHECK((status='PROPOSED' AND reviewed_by IS NULL AND approved_by IS NULL)
   OR (status='REVIEWED' AND reviewed_by IS NOT NULL AND approved_by IS NULL)
   OR (status='APPROVED' AND reviewed_by IS NOT NULL AND approved_by IS NOT NULL)
   OR (status='REJECTED')),
 CHECK((reviewed_by IS NULL) = (reviewed_at IS NULL)),
 CHECK((approved_by IS NULL) = (approved_at IS NULL))
);
CREATE UNIQUE INDEX uq_edarms_active_disposition_record
 ON edarms_disposition_case(tenant_id,record_id)
 WHERE status IN ('PROPOSED','REVIEWED','APPROVED');

CREATE TABLE edarms_disposition_event (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 case_id uuid NOT NULL,
 actor_sub text NOT NULL,
 action text NOT NULL CHECK(action IN ('PROPOSED','REVIEWED','APPROVED','REJECTED')),
 reason text NOT NULL CHECK(length(trim(reason)) >= 4),
 created_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(tenant_id,case_id) REFERENCES edarms_disposition_case(tenant_id,id)
);

CREATE OR REPLACE FUNCTION edarms_guard_hold_mutation() RETURNS trigger AS $$
BEGIN
 IF TG_OP = 'DELETE' THEN
  RAISE EXCEPTION 'Legal holds cannot be deleted';
 END IF;
 IF OLD.status <> 'ACTIVE' OR NEW.status <> 'RELEASED'
   OR NEW.tenant_id IS DISTINCT FROM OLD.tenant_id
   OR NEW.case_ref IS DISTINCT FROM OLD.case_ref
   OR NEW.legal_basis IS DISTINCT FROM OLD.legal_basis
   OR NEW.owner_sub IS DISTINCT FROM OLD.owner_sub
   OR NEW.approved_by IS NULL OR NEW.approved_by = OLD.owner_sub
   OR NEW.released_at IS NULL THEN
   RAISE EXCEPTION 'Only independently approved legal hold release allowed';
 END IF;
 RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_guard_hold BEFORE UPDATE OR DELETE ON legal_hold
FOR EACH ROW EXECUTE FUNCTION edarms_guard_hold_mutation();
CREATE TRIGGER trg_edarms_guard_hold_scope BEFORE UPDATE OR DELETE ON legal_hold_scope
FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();

CREATE OR REPLACE FUNCTION edarms_protect_original() RETURNS trigger AS $$
BEGIN
 RAISE EXCEPTION 'Original archive version is immutable';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_version_immutable BEFORE UPDATE OR DELETE ON record_version
 FOR EACH ROW EXECUTE FUNCTION edarms_protect_original();

CREATE OR REPLACE FUNCTION edarms_protect_record() RETURNS trigger AS $$
BEGIN
 IF TG_OP = 'DELETE' THEN
  RAISE EXCEPTION 'Record delete requires separate Bank-authorized execution';
 END IF;
 IF NEW.tenant_id IS DISTINCT FROM OLD.tenant_id THEN
  RAISE EXCEPTION 'Record ownership cannot change';
 END IF;
 IF OLD.status <> 'DRAFT' AND
  (NEW.title IS DISTINCT FROM OLD.title
   OR NEW.class_id IS DISTINCT FROM OLD.class_id
   OR NEW.metadata IS DISTINCT FROM OLD.metadata
   OR NEW.created_by IS DISTINCT FROM OLD.created_by
   OR NEW.record_no IS DISTINCT FROM OLD.record_no
   OR NEW.security_level IS DISTINCT FROM OLD.security_level) THEN
  RAISE EXCEPTION 'Declared record cannot be rewritten';
 END IF;
 RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_protect_record BEFORE UPDATE OR DELETE ON record
FOR EACH ROW EXECUTE FUNCTION edarms_protect_record();
-- Existing historic DISPOSED rows remain quarantined pending provenance;
-- new transitions to DISPOSED are not allowed before an approved execution engine.
ALTER TABLE record ADD CONSTRAINT ck_edarms_no_unapproved_disposal
 CHECK(status <> 'DISPOSED') NOT VALID;
ALTER TABLE disposition_batch ADD CONSTRAINT ck_edarms_no_batch_execution
 CHECK(status <> 'EXECUTED') NOT VALID;

CREATE TRIGGER trg_edarms_jra_evidence_immutable
 BEFORE UPDATE OR DELETE ON edarms_jra_evidence
 FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();
CREATE TRIGGER trg_edarms_hold_event_immutable
 BEFORE UPDATE OR DELETE ON edarms_hold_event
 FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();
CREATE TRIGGER trg_edarms_disposition_event_immutable
 BEFORE UPDATE OR DELETE ON edarms_disposition_event
 FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();

ALTER TABLE edarms_jra_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_jra_evidence FORCE ROW LEVEL SECURITY;
ALTER TABLE edarms_hold_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_hold_event FORCE ROW LEVEL SECURITY;
ALTER TABLE edarms_disposition_case ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_disposition_case FORCE ROW LEVEL SECURITY;
ALTER TABLE edarms_disposition_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_disposition_event FORCE ROW LEVEL SECURITY;
CREATE POLICY jra_evidence_tenant ON edarms_jra_evidence
 USING (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid);
CREATE POLICY hold_event_tenant ON edarms_hold_event
 USING (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid);
CREATE POLICY disposition_case_tenant ON edarms_disposition_case
 USING (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid);
CREATE POLICY disposition_event_tenant ON edarms_disposition_event
 USING (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid)
 WITH CHECK (tenant_id=nullif(current_setting('edarms.tenant_id',true),'')::uuid);

GRANT SELECT ON edarms_jra_evidence TO edarms_runtime;
GRANT SELECT,INSERT ON edarms_hold_event TO edarms_runtime;
GRANT SELECT,INSERT,UPDATE ON legal_hold TO edarms_runtime;
GRANT SELECT,INSERT ON legal_hold_scope TO edarms_runtime;
GRANT SELECT,INSERT,UPDATE ON edarms_disposition_case TO edarms_runtime;
GRANT SELECT,INSERT ON edarms_disposition_event TO edarms_runtime;
GRANT USAGE ON SEQUENCE edarms_hold_event_id_seq TO edarms_runtime;
GRANT USAGE ON SEQUENCE edarms_disposition_event_id_seq TO edarms_runtime;
    """)


def downgrade():
    raise RuntimeError("Bank archival governance history cannot be downgraded automatically")
