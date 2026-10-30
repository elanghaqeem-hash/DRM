"""Initial DRM relational model + tamper-evident DB audit ledger (PoC)."""
from alembic import op

revision = "0001_core_and_audit"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # No real Bank records, metadata, or retention durations are seeded.
    op.execute("""
CREATE TABLE classification_scheme (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL,
 name text NOT NULL, version integer NOT NULL CHECK(version > 0),
 effective_from date, effective_to date,
 approval_status text NOT NULL DEFAULT 'DRAFT'
 CHECK(approval_status IN ('DRAFT','PENDING','APPROVED','REJECTED')),
 proposed_by text, approved_by text, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(code,version),
 CHECK(approved_by IS NULL OR (proposed_by IS NOT NULL AND approved_by <> proposed_by))
);
CREATE TABLE retention_rule (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL,
 version integer NOT NULL CHECK(version > 0), active_period jsonb, inactive_period jsonb,
 trigger_type text NOT NULL CHECK(trigger_type IN ('CREATED','CLOSED','EVENT')),
 event_code text, final_action text NOT NULL CHECK(final_action IN ('DESTROY','PERMANENT','TRANSFER')),
 legal_basis text, approval_status text NOT NULL DEFAULT 'DRAFT'
 CHECK(approval_status IN ('DRAFT','PENDING','APPROVED','REJECTED')),
 proposed_by text, approved_by text,
 CHECK(approved_by IS NULL OR (proposed_by IS NOT NULL AND approved_by <> proposed_by)),
 CHECK(trigger_type <> 'EVENT' OR event_code IS NOT NULL),
 UNIQUE(code,version)
);
CREATE TABLE record_class (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 scheme_id uuid NOT NULL REFERENCES classification_scheme(id),
 code text NOT NULL, name text NOT NULL, parent_id uuid REFERENCES record_class(id),
 required_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
 retention_rule_id uuid REFERENCES retention_rule(id),
 security_default text NOT NULL, effective_from date, effective_to date,
 UNIQUE(scheme_id,code)
);
CREATE TABLE aggregation (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parent_id uuid REFERENCES aggregation(id),
 code text NOT NULL UNIQUE, title text NOT NULL, owner_unit text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE record (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), record_no text NOT NULL UNIQUE,
 class_id uuid NOT NULL REFERENCES record_class(id), title text NOT NULL,
 security_level text NOT NULL, status text NOT NULL DEFAULT 'DRAFT'
 CHECK(status IN ('DRAFT','DECLARED','ON_HOLD','DISPOSED')),
 vital_flag boolean NOT NULL DEFAULT false,
 contains_personal_data boolean NOT NULL DEFAULT false,
 owner_unit text NOT NULL, metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
 retention_trigger_date date, retention_due_date date, created_by text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), declared_at timestamptz
);
CREATE TABLE record_aggregation (
 record_id uuid NOT NULL REFERENCES record(id),
 aggregation_id uuid NOT NULL REFERENCES aggregation(id),
 PRIMARY KEY(record_id,aggregation_id)
);
CREATE TABLE record_version (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), record_id uuid NOT NULL REFERENCES record(id),
 major_version integer NOT NULL CHECK(major_version > 0),
 minor_version integer NOT NULL DEFAULT 0 CHECK(minor_version >= 0),
 object_key text NOT NULL UNIQUE, mime text NOT NULL, size_bytes bigint NOT NULL CHECK(size_bytes >= 0),
 sha256 char(64) NOT NULL, ocr_text_ref text, preservation_format text,
 created_by text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(record_id,major_version,minor_version)
);
CREATE TABLE physical_location (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE,
 name text NOT NULL, kind text NOT NULL
 CHECK(kind IN ('BUILDING','ROOM','SHELF','BOX','FOLDER')),
 parent_id uuid REFERENCES physical_location(id)
);
CREATE TABLE physical_item (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), record_id uuid NOT NULL REFERENCES record(id),
 barcode text NOT NULL UNIQUE, location_id uuid NOT NULL REFERENCES physical_location(id),
 condition_note text, last_verified_at timestamptz
);
CREATE TABLE loan (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), record_id uuid NOT NULL REFERENCES record(id),
 media text NOT NULL CHECK(media IN ('PHYSICAL','DIGITAL')),
 borrower_sub text NOT NULL, approver_sub text, due_at timestamptz NOT NULL,
 status text NOT NULL DEFAULT 'REQUESTED'
 CHECK(status IN ('REQUESTED','APPROVED','CHECKED_OUT','RETURNED','DENIED','EXPIRED')),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE legal_hold (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), case_ref text NOT NULL,
 legal_basis text NOT NULL, owner_sub text NOT NULL,
 status text NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','REVIEW','RELEASED')),
 next_review_at timestamptz, released_at timestamptz, approved_by text,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE legal_hold_scope (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), hold_id uuid NOT NULL REFERENCES legal_hold(id),
 record_id uuid REFERENCES record(id), saved_query jsonb,
 CHECK((record_id IS NOT NULL) <> (saved_query IS NOT NULL))
);
CREATE TABLE disposition_batch (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), reference_no text UNIQUE,
 status text NOT NULL DEFAULT 'PROPOSED'
 CHECK(status IN ('PROPOSED','REVIEWING','APPROVED','EXECUTED','REJECTED')),
 proposed_by text NOT NULL, reviewed_by text, approved_by text, executed_by text,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(reviewed_by IS NULL OR reviewed_by <> proposed_by),
 CHECK(approved_by IS NULL OR approved_by NOT IN (proposed_by,coalesce(reviewed_by,''))),
 CHECK(executed_by IS NULL OR executed_by NOT IN
 (proposed_by,coalesce(reviewed_by,''),coalesce(approved_by,'')))
);
CREATE TABLE disposition_item (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), batch_id uuid NOT NULL REFERENCES disposition_batch(id),
 record_id uuid NOT NULL REFERENCES record(id), decision text, execution_result jsonb,
 UNIQUE(batch_id,record_id)
);
CREATE TABLE disposition_certificate (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 batch_id uuid NOT NULL UNIQUE REFERENCES disposition_batch(id),
 certificate_ref text NOT NULL, object_key text NOT NULL, sha256 char(64) NOT NULL,
 signed_at timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE access_request (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), record_id uuid REFERENCES record(id),
 requester_sub text NOT NULL, requester_category text NOT NULL
 CHECK(requester_category IN ('INTERNAL','CUSTOMER','AUDITOR','OJK','LAW_ENFORCEMENT')),
 legal_basis text NOT NULL, status text NOT NULL DEFAULT 'REQUESTED',
 approved_by text, proof_ref text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE pdp_processing_register (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), class_id uuid NOT NULL REFERENCES record_class(id),
 personal_data_categories jsonb NOT NULL DEFAULT '[]', purpose text,
 legal_basis text, controller_owner text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE data_subject_request (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), subject_ref text NOT NULL,
 request_type text NOT NULL CHECK(request_type IN ('ACCESS','RECTIFY','ERASE','OBJECT','OTHER')),
 status text NOT NULL DEFAULT 'RECEIVED', decision_basis text,
 dpo_reviewer text, requested_at timestamptz NOT NULL DEFAULT now(),
 closed_at timestamptz
);
CREATE TABLE role (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, description text
);
CREATE TABLE permission (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, description text
);
CREATE TABLE role_permission (
 role_id uuid NOT NULL REFERENCES role(id), permission_id uuid NOT NULL REFERENCES permission(id),
 PRIMARY KEY(role_id,permission_id)
);
CREATE TABLE user_attribute (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), oidc_subject text NOT NULL,
 attr_key text NOT NULL, attr_value text NOT NULL, UNIQUE(oidc_subject,attr_key)
);
CREATE TABLE access_review_campaign (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), title text NOT NULL,
 status text NOT NULL DEFAULT 'DRAFT', due_at timestamptz, created_by text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE audit_event (
 seq bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 event_id uuid NOT NULL UNIQUE, ts timestamptz NOT NULL,
 actor_sub text NOT NULL, actor_role text NOT NULL, source_ip text,
 device text, action text NOT NULL, object_ref text NOT NULL,
 before_hash text, after_hash text, result text NOT NULL,
 prev_hash char(64) NOT NULL, event_hash char(64) NOT NULL UNIQUE,
 payload jsonb NOT NULL
);
CREATE INDEX ix_audit_event_ts ON audit_event(ts);
CREATE INDEX ix_audit_event_object ON audit_event(object_ref);
CREATE OR REPLACE FUNCTION reject_audit_mutation() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'audit_event is append-only; changes are prohibited'; END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_audit_no_update BEFORE UPDATE OR DELETE ON audit_event
FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
    """)


def downgrade():
    raise RuntimeError("Irreversible: Bank record and audit data must not be dropped automatically")
