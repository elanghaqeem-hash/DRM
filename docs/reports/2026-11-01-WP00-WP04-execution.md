# WP00–WP04 EDARMS critical-path execution evidence — 2026-11-01

**Scope:** executable code & synthetic CI test infrastructure. **Bank production:** NOT APPROVED. **Bank JRA, signed SOP, IdP federation, real immutable storage and DR:** NOT VERIFIED.

## Repository chain of custody
- Single source of truth: https://github.com/elanghaqeem-hash/DRM
- Branch: `feature/edarms-critical-path-wp00-wp04-20261101`; based on CI-passing WP0/WP1 branch.
- Review PR #4: https://github.com/elanghaqeem-hash/DRM/pull/4 (draft until code review and CI).
- Existing PR #2 targets main but remains unmerged; pre-existing PR #3 targets WP1 branch and is **divergent** with an alternate Alembic 0003 revision. Never merge both in arbitrary order; reconcile graph and tests first.

## WP00: requirement control and honest UAT evidence
- `infra/scripts/action_evidence.py` reads the canonical 62-submenu/414-action CSV and reports actual statuses without conflating design entries with Bank PASS.
- `--production-gate` exits nonzero if any of 414 actions lacks credible signed Bank UAT evidence or the approved API/permission contract. No action is considered verified currently.
- Next: acquire signed Bank BRD/metadata/JRA/IAM/role/records authority/retention schedule and publish the official test traceability matrix. No guessed retention periods.

## WP01: tenant/security foundation
- Reuses existing 0003: FORCE RLS on 24 legacy tables, unknown legacy ownership remains quarantined; application connects via non-superuser non-BYPASSRLS runtime DB role. **Existing NOT VALID tenant FKs and real Bank provenance still require signed reconciliation.**
- Sensitive legal hold and disposition routes call the signed-token MFA assurance checker, which must be configured to require Bank-approved ACR/AMR. **PoC default may accept non-MFA synthetic tokens, so Bank IdP integration is NOT proven.**
- Database controls prevent direct record DISPOSED and legacy batch EXECUTED state changes; preserve original record versions from mutation.

## WP02/WP03: records foundation
- Retains classification, record series, metadata and record_version schema from WP1. New appraisal requires approved classification and at least one version.
- Secure AV and S3 Object Lock adapters already exist but are not active as a real capture API; externally verified quarantine, signature updates, private object storage/KMS, retention scheduling and original readback remain next build gates.
- No false claim of end-to-end capture/declaration or 62 finished UI routes.

## WP04: new governed retention and legal/disposition workflow
- Alembic `0004_governed_records`: tenant-scope Bank JRA evidence register with no application write grant, hold event ledger, multi-stage disposition cases/events, RLS policies, immutable event triggers, hold owner-release independence, original immutable version and fail-closed legacy status constraints.
- `services/retention/decision.py`: deterministic reasons for refusal: non-declared, vital, no original, unapproved classification, immature/missing JRA, no signed evidence registration, active record or unresolved dynamic tenant hold.
- `services/retention/governed.py`: signed-actor/tenant membership via _start_scope; advisory record locks serialize hold vs disposition transitions; apply/independent release of multiple holds, proposal → reviewed → independently approved. Every decision rechecks current retention/hold.
- FastAPI: `GET /v1/archives/{id}/retention-preview`; `POST /v1/archives/{id}/legal-holds`; `POST /v1/legal-holds/{id}/release`; `POST /v1/dispositions`; `POST /v1/dispositions/{id}/decision`.
- **APPROVED only means internal REVIEW APPROVAL, never deletion**. No physical object deletion endpoint, certificate issuance, permanent transfer or legally effective disposition was implemented. Bank approval registry rows must be provisioned through controlled verified admin process, not via public API.

## Synthetic tests and restoration evidence
- `tests/unit/test_governed_appraisal.py` exercises adverse retention/hold/JRA/immutable-original policy.
- `tests/integration/test_governed_archive.py` exercises actual Postgres roles, RLS, multiple holds and legal release, SoD, JRA read-only attestation, proposal lifecycle, recheck if hold applied after proposal and DB mutation denials.
- `infra/scripts/verify_restore.py` checks backup manifests for three components (database/objects/audit), checks SHA256/byte size/path safety, refuses non-isolated or nonempty target and runs `pg_restore` only on a specifically prefixed disposable DB.
- `tests/integration/test_synthetic_restore.py` executes a real `pg_dump` to isolated `pg_restore` plus record/version/hold/audit count reconciliation; uses synthetic placeholder object and audit files. **This is NOT live Bank DR proof**: real encrypted object restoration, immutable audit anchor verification, recovery time objective measurement, network key recovery and signed Bank test absent.
- Running `pytest -m integration -q` on CI establishes synthetic database evidence only after latest run PASS. A green `quality`/unit job is not Bank signoff.

## Next critical execution queue
1. Close CI failures and log passing commit SHA. Confirm original record and hold invariants through DB integration.
2. Build WP02 approved metadata/classification APIs with effective-dated Bank-owned policies and maker/checker.
3. Complete WP03 capture→quarantine→AV→QA→ObjectLock→declaration→search under Bank-approved KMS; integration test with actual services, not mocks.
4. Add e-signature evidence, Bank-approved JRA import and annual reviews; signed independent disposition certificates and execution only after external production release.
5. Formal bank IdP positive+negative UAT; full cross-tenant matrix for API/search/export/workers/object URLs.
6. Run Bank DR rehearsal using **actual approved isolated environment** (DB + object content + audit anchor + KMS), measure RPO/RTO and obtain signed Risk/IT/Compliance/Records acceptance.
7. Implement remaining 62 submenu / 414 action contracts per WP05–WP09, each with authenticated API, persisted state, audit, negative UAT and Bank acceptance.
8. Produce code/release reconciliation for PR #2, #3 and #4, no blind merge of competing Alembic 0003 revisions.

## Go/no-go
**NO-GO** for real Bank data, legal destruction and production deployment until external P0 release gates pass. No Bank secrets, actual approved JRA, operational IdP/bucket/ClamAV, source-system data or Bank DR environment were available during this run.

## Subsequent WP02 controlled-draft vertical slice (same implementation branch)
- Alembic `0005_controlled_drafts` now enforces tenant + signed actor provenance, approved classification, required metadata configuration, security defaults and **draft-only** status at database INSERT boundary; generates append-only metadata digest events and restricts app runtime to INSERT drafts, not content versions or record declarations.
- `services/records/drafts.py` and API `GET /v1/records/classes`, `POST /v1/records/drafts`: DB-backed approved file plan lookup and authenticated draft creation, provisional DRAFT identifiers only; never issues official Bank archive numbering or asserts capture/AV/WORM success.
- `tests/integration/test_governed_drafts.py` adds synthetic positive/negative PostgreSQL tests for mandatory metadata, cross-tenant denial, unauthorized role, draft event, and rejection of attempts to insert DECLARED originals directly.
- Full WP02 master-data governance (draft→review→approve→effective version) and full WP03 file capture are **NOT COMPLETE**. Keep physical content uploading, QA declaration and official numbering disabled pending Bank rules and actual protected storage integration.
