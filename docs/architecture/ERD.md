# EDARMS Conceptual ERD and WP1 Data Boundary

**Architecture design, not an assertion that all target tables exist.** Existing Sprint 0 migration 0001 contains legacy PoC record tables WITHOUT tenant scope. They are not approved for cross-Bank content and are excluded from the new WP1 workspace feature.

~~~mermaid
erDiagram
  EDARMS_TENANT ||--o{ EDARMS_MEMBERSHIP : grants
  EDARMS_TENANT ||--o{ EDARMS_REVIEW_TASK : scopes
  EDARMS_REVIEW_TASK ||--o{ EDARMS_TASK_EVENT : records
  TENANT ||--o{ RECORD_SERIES : defines
  RECORD_SERIES ||--o{ CASE_FILE : groups
  CASE_FILE ||--o{ RECORD : contains
  RECORD ||--o{ IMMUTABLE_VERSION : preserves
  IMMUTABLE_VERSION ||--o{ REPRESENTATION : derives
  RECORD ||--o{ HOLD_SCOPE : protected_by
  LEGAL_HOLD ||--o{ HOLD_SCOPE : covers
  DISPOSITION_BATCH ||--o{ DISPOSITION_ITEM : includes
  RECORD ||--o{ DISPOSITION_ITEM : appraises
~~~

## Target service model
Browser (Bank OIDC/PKCE, MFA) -> typed API -> per-tenant membership + resource authorization -> PostgreSQL scoped transaction/row security -> audit and transactional outbox -> private object storage with checksum, versioning/retention and KMS. Asynchronous sandboxed malware/OCR/fixity workers. Search and signed downloads repeat ACL; SIEM and independent audit WORM anchor before production.

## Actual WP1 isolated slice
- edarms_tenant: no tenant or Bank data seeded.
- edarms_membership: OIDC subject + tenant + enabled scoped role, separate from JWT global roles.
- edarms_review_task: tenant-scoped generic review inbox, unique idempotency key, optimistic version, assigned checker, maker != checker, PostgreSQL FORCE RLS.
- edarms_task_event: append-only workflow evidence written in same transaction as state mutation. External immutable anchor not implemented; this is **not** production grade WORM.
- API exposed only to independently authenticated OIDC subjects. The legacy record table and legacy audit API still need tenant-aware redesign; do not connect Bank content.
- Generic task decisions do **not** authorize archive declaration, legal hold release or destruction.

## Bank acceptance gates
Select hosting/residency, tenant isolation model, IdP/MFA and provisioning, KMS/object custody, RPO/RTO, record-series schema and legal JRA; implement migration and restore before real Bank data. Any default RLS bypass role (including superuser) must be excluded from application credentials; database owner and out-of-band audit must be separated.
