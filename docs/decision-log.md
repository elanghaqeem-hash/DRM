# Decision Log — DRM

## ADR-0001 — GitHub as source of truth
- 2026-10-30; accepted. Repository elanghaqeem-hash/DRM and explicit commits
  are the source of implementation evidence. A chat alone does not push code.

## ADR-0002 — Controlled PoC technology baseline
- 2026-10-30; accepted for PoC only. Python 3.12/FastAPI with PostgreSQL 16,
  Keycloak, MinIO and Docker Compose. Bank stack and platform remain TBD-BANK.

## ADR-0003 — No inferred retention schedule
- 2026-10-30; accepted. All retention durations, event definitions, numbering and
  classification are controlled by Bank owners. Never seed fabricated legal periods.

## ADR-0004 — Audit chain limitations
- 2026-10-30; accepted. Database append-only trigger and hash chain do not provide
  WORM protection from a privileged DBA. External immutable checkpoints and
  separately controlled credentials remain a production gate.

## ADR-0005 — Sprint 1 no-policy-bypass starter
- 2026-10-30; accepted for PoC. Rule helpers reject empty/invalid mandatory
  metadata configuration, self-approval and editing a declared/held/disposed record.
  Full transactional API and object storage lock remain unimplemented.

## ADR-0006 — Regulatory and traceability review
- 2026-10-30; pending. Source proposal DOC-20261028-WA0060.pdf not available for
  direct PED/CTL reconciliation in this work session; confirm before acceptance.
