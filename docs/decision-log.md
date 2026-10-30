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


## ADR-0007 — Continuity across diverged branches (2026-10-30)
- **Status:** Accepted for PoC only. Main HEAD 4a8f07ecd1a8368d91d8bdaa2ca281330dd89bdb held EDARMS docs, while feature/sprint0-foundation HEAD 02555dff4f7d6a360b2e03fe373d48873e70a053 held FastAPI/PostgreSQL PoC. Use feature base and explicitly import main's master/audit without resetting history. Retain FastAPI for existing PoC; Bank production technology selection is TBD-BANK.

## ADR-0008 — Isolated generic review task pilot (2026-10-30)
- **Status:** Accepted for synthetic PoC only. New tenant+membership+generic task tables enforce PostgreSQL FORCE RLS, JWT subject checked against enabled scoped membership, assigned independent checker, optimistic version, idempotency, and task event persistence within same transaction. No real bank tenants seeded.
- **Limitations:** Existing record and audit tables are not tenant-safe. New task event evidence is DB append-only only, not external WORM. Approval of generic task must not be interpreted as record/deletion authority. Production remains blocked.

## ADR-0009 — Do not bypass secret scanning (2026-10-30)
- **Status:** Accepted. Workflow run 41007380254: integration SUCCESS; quality Gitleaks FAILURE because shallow history did not contain requested scan revision (0 bytes scanned). Checkout full history, re-run and verify actual Gitleaks pass; never suppress scanner failure.
