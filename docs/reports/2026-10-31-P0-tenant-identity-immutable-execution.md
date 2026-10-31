# EDARMS P0 execution evidence — 31 Oct 2026

## Scope executed (WP1 continuation; synthetic sandbox only)

### P0-1 legacy tenant isolation

- Migration `0003_legacy_tenant_envelope`: adds `tenant_id` to 24 legacy tables, enables **FORCE RLS** on all 24 and existing tenant/membership tables; tenant-unknown pre-existing rows are invisible (quarantined); `NOT VALID` tenant-required checks reject future tenant-less inserts without fabricating historical ownership; composite tenant FKs reject cross-tenant references in 21 relations.
- Runtime role `edarms_runtime` is NOLOGIN/NOBYPASSRLS, API login provisioned separately from schema owner via `infra/scripts/provision_runtime.py`. API Compose connection uses `RUNTIME_DATABASE_URL`, not migration-owner URL; readiness and workspace endpoints reject superuser/BYPASSRLS DB identities. `Dockerfile` now includes required web assets and provisioning script.
- Existing legacy audit is tenant-scoped for new entries; old unattributed audit rows are quarantined. Appends use per-tenant serial hash chain; audit verify requires signed JWT role plus scoped DB membership.
- `infra/scripts/legacy_tenant_report.py` reports only aggregate unmapped historical row counts, exits non-zero if any remain. **No migration assigns actual legacy records to any Bank tenant**. Bank-approved provenance/mapping, reconciled counts and FK validation remain required before operational access.
- Negative PostgreSQL tests: all legacy RLS tables, unknown/missing tenant, cross-tenant record FK, direct record ID isolation under non-BYPASSRLS login, audit chain isolation, maker/checker.

### P0-2 identity, antivirus and immutable object storage

- OIDC access token signature, audience and issuer validation retained; configurable signed `acr`/`amr` enforcement with recent `auth_time` added to sensitive audit write and task decision. Staging requires explicit Bank-approved MFA claim values and MFA enabled. Local synthetic token claim tests added.
- `services/storage/immutable_ingest.py`: ClamAV INSTREAM TCP adapter denies unsafe size, malware, scanner downtime or missing verdict; S3-compatible Object Lock adapter verifies enabled bucket, writes COMPLIANCE-locked version with future `retain_until`, and reads back retention, version, tenant metadata and SHA-256 checksum. No silent fallback.
- Unit tests use fake scanner/socket and object store. **No Bank IdP federation, hardware MFA, actual AV engine/bucket, vault/HSM, verified retention schedule, immutable external audit anchor or live verification occurred.** Immutable adapter is intentionally *not* exposed through a public records ingestion endpoint until JRA, validation and approvals exist.

## Verification / caveats

- Latest GitHub CI run and logs are the test evidence; verify conclusion on latest commit. Do not infer successful UAT from unit mocks.
- The legacy schema is designed to fail closed. For real Bank data: obtain approved record-level tenant provenance, map historical rows in supervised transaction, reconcile counts, validate `NOT VALID` constraints and cross-tenant foreign keys, run read/write/export negative tests across all data paths.
- The API PoC now requires runtime DB role provisioning; on existing persistent environments, rotate credentials via protected procedure and verify backup before upgrade.
- 62 submenu / 414 actions remain mostly design-only. JRA, legal hold, disposition, complete records API, Bank SSO/MFA, external WORM/AV and restore end-to-end UAT are NOT FINISHED.
- **Production startup remains intentionally blocked. No production release or Bank data processing authorized.**

## Bank-owned release blockers

1. Identity team: IdP metadata, issuer/audience signing keys, role mapping, MFA `acr`/`amr` assurance, session revocation and UAT users.
2. Records/Legal: approved JRA version and signed classifications; legal hold precedence and disposition authority.
3. Security/Infra: compliant Object Lock bucket, verified ClamAV service & malware signatures, KMS/HSM, network controls, independent VA/PT.
4. DBA/Data Owner: signed tenant provenance for all historical records, quarantine reconciliation, data integrity report and restore rehearsal.
5. Bank Risk/IT/Compliance: UAT evidence and production release approval.

See `docs/reports/2026-10-31-enterprise-release-gates.md`.
