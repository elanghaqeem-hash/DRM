"""Tenant-scoped generic review inbox; legacy records remain PoC only."""
from alembic import op

revision = "0002_tenant_workspace"
down_revision = "0001_core_and_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE edarms_tenant (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 code text NOT NULL UNIQUE CHECK(length(code) BETWEEN 2 AND 40),
 name text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE edarms_membership (
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 actor_sub text NOT NULL CHECK(length(actor_sub) BETWEEN 1 AND 255),
 role_code text NOT NULL CHECK(role_code IN
  ('records_officer','records_manager','approver','auditor')),
 enabled boolean NOT NULL DEFAULT false,
 PRIMARY KEY (tenant_id,actor_sub,role_code)
);
CREATE TABLE edarms_review_task (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 title text NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 180),
 created_by text NOT NULL,
 assigned_to text NOT NULL,
 idempotency_key text NOT NULL CHECK(length(idempotency_key) BETWEEN 8 AND 128),
 status text NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','APPROVED','REJECTED')),
 version integer NOT NULL DEFAULT 1 CHECK(version > 0),
 decision_reason text,
 decided_by text,
 decided_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE (tenant_id,created_by,idempotency_key),
 CHECK ((status = 'OPEN' AND decided_by IS NULL AND decided_at IS NULL)
   OR (status <> 'OPEN' AND decided_by IS NOT NULL AND decided_at IS NOT NULL)),
 CHECK (decided_by IS NULL OR decided_by <> created_by)
);
CREATE INDEX ix_edarms_task_inbox ON edarms_review_task
 (tenant_id,assigned_to,status,created_at DESC);
CREATE TABLE edarms_task_event (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 tenant_id uuid NOT NULL REFERENCES edarms_tenant(id),
 task_id uuid NOT NULL REFERENCES edarms_review_task(id),
 actor_sub text NOT NULL,
 action text NOT NULL CHECK(action IN ('CREATED','APPROVED','REJECTED')),
 reason text,
 occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE OR REPLACE FUNCTION edarms_reject_event_mutation() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'Task history is append-only'; END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_edarms_task_event_immutable
 BEFORE UPDATE OR DELETE ON edarms_task_event
 FOR EACH ROW EXECUTE FUNCTION edarms_reject_event_mutation();
ALTER TABLE edarms_review_task ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_review_task FORCE ROW LEVEL SECURITY;
CREATE POLICY edarms_task_scope ON edarms_review_task
 USING (tenant_id = NULLIF(current_setting('edarms.tenant_id', true),'')::uuid)
 WITH CHECK (tenant_id = NULLIF(current_setting('edarms.tenant_id', true),'')::uuid);
ALTER TABLE edarms_task_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE edarms_task_event FORCE ROW LEVEL SECURITY;
CREATE POLICY edarms_event_scope ON edarms_task_event
 USING (tenant_id = NULLIF(current_setting('edarms.tenant_id', true),'')::uuid)
 WITH CHECK (tenant_id = NULLIF(current_setting('edarms.tenant_id', true),'')::uuid);
    """)


def downgrade():
    raise RuntimeError("No automatic drop of tenant task or audit evidence")
