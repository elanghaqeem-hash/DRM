# EDARMS Security-Hardening Execution — 31 October 2026

**Status: PARTIAL — synthetic PoC only, NOT Bank production/UAT or compliance certification.**
Repository: https://github.com/elanghaqeem-hash/DRM
Branch: `feature/edarms-wp2-record-isolation-20261031`
Draft PR: https://github.com/elanghaqeem-hash/DRM/pull/3 (base: WP0/WP1 feature branch).
Source of requirements: `docs/prompts/MASTER-PROMPT-EDARMS-ENTERPRISE-2026-10-30.md`.

## Completed code artifacts (to be checked on each final CI run)

1. Migration `0003_archive_tenant_isolation` scopes **18 legacy business tables** by non-null tenant IDs, RLS/FORCE RLS and parent-child composite foreign keys. Fail-fast if any legacy table already contains data; **does not backfill or silently assign existing Bank documents**. Audit-global endpoint is disabled by default; legacy `audit_event` migration requires a separately approved chain-preserving procedure.
2. Runtime non-owner `edarms_runtime` SQL role provisioned through separate migration container, with limited grants, no BYPASSRLS/superuser/owner privileges. Docker Compose now removes migration-admin credentials from API environment. Static `/app` assets are packaged in Docker.
3. Declarative DB triggers prohibit record_version update/delete, declared record content rewrite or record deletion; no direct `DISPOSED` / `EXECUTED` state until formally authorized disposal engine.
4. Genuine tenant-scoped retention appraisal API and independently issued/released legal holds with append-only events; multiple holds stay active independently; unresolved query holds block disposal evaluations. Dynamic JRA action **never destroys records**; JRA applicability and Bank signatures remain unverified.
5. Bank OIDC ACR assurance enforcement capability: signed JWT requires configured exact `OIDC_REQUIRED_ACR`. Actual Bank IdP federation and live MFA challenge test **NOT RUN**, as Bank issuer, client, metadata, test identities and policy approval are absent.
6. ClamAV INSTREAM adapter, private S3 Object Lock (COMPLIANCE), KMS encryption and download checksum verification: fail-closed secure capture contract with negative tests. **NO live antivirus engine, private bucket, Bank KMS, signed object retention or upload API verified**.
7. Restore manifest checker enforces database + object + audit hash completeness and blocks traversal/tamper; guarded `pg_restore` runner refuses a non-isolated target DB and can reconcile restored record/hold/audit counts. Actual isolated restoration with authentic DB/blob/audit backup **NOT RUN**; independent WORM audit verification pending.
8. UI PoC adds authentic read-only retention preview and Legal-controlled hold apply/release for synthetic record IDs; role/tenant membership and database checks are enforced server-side.
9. CI executes Python unit, disposable PostgreSQL integration, Ruff/Bandit/pip-audit/Gitleaks, JS syntax, Keycloak JSON validity, and now Docker image + Compose configuration build.

## 62-submenu truth in present branch

| Group | Total submenus | Status |
|---|---:|---|
| A Executive & Workspace | 4 | A2 task inbox PoC PARTIAL, others NOT BUILT |
| B Governance & Classification | 6 | Database/invariants only; screens NOT BUILT |
| C Correspondence & Digital Records | 8 | Immutable schema and ingest adapter only; end-to-end NOT BUILT |
| D Physical Archives | 5 | Legacy tables scoped; screens/workflows NOT BUILT |
| E Search & Requests | 4 | NOT BUILT |
| F Retention, Hold & Disposition | 7 | F2 preview and F3 legal hold PoC PARTIAL; legal JRA/execution NOT BUILT |
| G Preservation, DR & Evidence | 4 | Verification tools only; Bank recovery NOT RUN |
| H Compliance & Reporting | 7 | Control documentation only; screens NOT BUILT |
| I AI/OCR | 5 | NOT BUILT; no AI destruction allowed |
| J Administration & Integration | 12 | IAM foundations only, others NOT BUILT |
| **TOTAL** | **62** | **No full menu group is enterprise-DONE** |

Master inventory contains **414 explicitly named actions**; these are requirements, not 414 functioning buttons. UI API PoC subsets (A2, F2, F3) cannot count as full 62 end-to-end releases. The 330 designed Bank UAT slots are not 330 executed test cases.

## Quality gates and security limitations

- All Bank-approval-dependent controls remain `TBD-BANK/VERIFY`; no fabricated 10-year JRA or approved retention rule.
- PostgreSQL migration intentionally refuses non-empty legacy tables. For live migration, Bank owner must approve per-record tenant mapping, secure snapshot, row counts/foreign-key reconciliation, parallel run, rollback and independent restore. No real backfill was attempted.
- Existing legacy hash-chain audit is not independently WORM anchored. New hold/control events are append-only but not tamper-proof against privileged DBA. Independent anchors and complete SIEM/audit evidence needed.
- Synthetic CI tests do not prove Bank identity provider MFA, data residency, real antivirus signatures, Object Lock governance/WORM retention, DR RPO/RTO, VA/PT or UI/browser UAT.
- `legacy_audit_api_enabled` defaults FALSE. No blanket cross-tenant audit viewer released.
- User-specific roles, JRA, legal dispositions, confidentiality labels, encryption keys, bank object storage, RPO/RTO, source systems and production cutover need Bank sign-off (Master TBD-BANK-001..020).

## Mandatory next release gates (not passed)

Bank identity federation + MFA with signed test vectors and logout/revocation; migration rehearsal using authorized legacy data; S3/KMS/AV live integrity tests; effective-dated, Bank-approved JRA and mandatory legal evidence; dual independent destruction approvers with hold race tests; immutable audit external anchors; restore of actual isolated DB, objects and audit; complete 62 menu UI/API actions and all P0 role/tenant tests; 330 scenario Bank UAT, VA/PT and IT/Legal/Records/Compliance sign-off.

**No production deployment, no merge to main, no Bank records ingested or destroyed.**
