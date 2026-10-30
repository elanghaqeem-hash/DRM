# Changelog — DRM

## [Unreleased] — 30 October 2026
### Added
- Imported PoC Sprint 0 API, PostgreSQL migration, OIDC authentication, audit hash chain,
  Docker Compose, migration workflow, tests, and CI configuration.
- Open Bank parameter register, provisional traceability and release gates.
- Sprint 1 control-driven pure record domain policies: classification approval,
  maker-checker, mandatory metadata and immutable record statuses.
### Known gaps
- No end-to-end UAT, PostgreSQL smoke test in this execution environment,
  production WORM, ABAC, KMS/HSM, or Bank-approved settings.
- Referenced source proposal PDF has not yet been reconciled.
- Final XLSX compliance matrix is not yet committed in this initial code import.
### Prior history
- Repository and AGENTS.md initialized as shared source of truth.


### EDARMS WP0 / WP1 (2026-10-30)
- Imported current EDARMS master prompt and enterprise audit from main to PoC-based working branch without deleting existing FastAPI code.
- Added verified audit baseline, draft BRD, VERIFY control matrix, conceptual ERD, 10 group/62 submenu navigation catalog, 414-action registry and 330 planned UAT slots (NOT RUN).
- Added migration 0002 tenant-scoped generic review tasks, membership, task history and FORCE RLS; implemented authorized inbox/create/decide API with idempotency, SoD and optimistic concurrency.
- Added domain and PostgreSQL integration tests; corrected Gitleaks checkout history issue. CI result must be observed before treating gate as PASS.
- Not done: UI/UX routes and 62 working screens, Bank IAM/MFA, tenant retrofit of legacy record/audit, AV/object storage, Bank JRA/legal hold/disposal, production and restore drill.
- Bank parameters remain TBD-BANK / VERIFY, WP0 Bank approval PENDING.
