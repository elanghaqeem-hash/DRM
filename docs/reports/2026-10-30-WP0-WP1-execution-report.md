# EDARMS — WP0 and WP1 Execution Evidence

**Report date:** 30 October 2026 (Asia/Jakarta). **Mode:** isolated synthetic PoC. **Repository:** https://github.com/elanghaqeem-hash/DRM. **Branch:** feature/edarms-wp0-wp1-20261030. **Review:** [draft PR #2](https://github.com/elanghaqeem-hash/DRM/pull/2). This report is not evidence of production, Bank UAT or legal approval.

## Repository baseline
- main HEAD at initial audit: 4a8f07ecd1a8368d91d8bdaa2ca281330dd89bdb.
- Existing Sprint-0 PoC branch: feature/sprint0-foundation HEAD 02555dff4f7d6a360b2e03fe373d48873e70a053. Code preserved: Python/FastAPI, PostgreSQL, Keycloak, MinIO/Redis Compose, Alembic 0001 and audit hash chain.
- Main had newer EDARMS master prompt/audit; feature and main had diverged. Integrated by explicit merge parent commit eb7dbbf5a7a96a5ae89fd990fb0bbe66ce8cec20. No force push, no overwrite of source, PR mergeable.

## WP0 — Discovery and planning
**Status: PARTIAL — documentation and technical inventory delivered; Bank review pending.**
- Imported official master prompt and original preliminary audit.
- Authored verified baseline, draft BRD/RACI/NFR, conceptual ERD, legal VERIFY matrix, UX inventory for 10 groups / 62 submenu / 414 explicitly named actions and UAT coverage skeleton 330 slots.
- 414 is an *inventory of named actions*, not 414 implemented buttons. 330 scenarios are a budget, not executable tests; scope and procedure need Bank sign-off.
- ADRs preserve existing FastAPI PoC, isolate tenant pilot, document security and CI risk.
- **Gate not satisfied:** Bank owner sign-off for TBD-BANK-001–020, effective approved JRA, legal applicability, architecture and data location, SSO/MFA/role policy, approved threat-model objectives.

## WP1 — Platform foundation
**Status: PARTIAL — one genuine task vertical slice and browser workspace; not full EDARMS.**
- Alembic 0002: edarms_tenant, membership, review_task, append-only task_event; DB FORCE RLS; unique idempotency key; optimistic version; maker/checker constraint. No Bank data/tenants seeded.
- FastAPI signed OIDC subject + DB membership; workspace me/list/create/approve/reject; role/tenant scope, denied self-approval, stale 409 and rejected reason mandatory.
- Web at /app: local PoC OIDC PKCE, accessible left collapsible sidebar/mobile drawer, tenant selection, real list/filters, create and approval/reject actions. All other planned menu groups explicitly unreleased; no dummy statistics.
- Keycloak new local-only public drm-web client, audience mapping (not proof of Bank federation). Front-channel logout clears browser token and tries IdP end-session; server-side revocation not implemented.
- Gitleaks false positive on *prose only* in imported master prompt was investigated using archived SARIF. Specific fingerprint ignored in .gitleaksignore; default detection and full-history scan remain active. No production secrets committed.

## Test evidence

[GitHub CI run 41031409696](https://github.com/elanghaqeem-hash/DRM/actions/runs/41031409696) — **PASS** for commit 87fcdf1e53630759aca76ed046e7e94e345a0e71 (before documentation-only follow-up):
- Python non-integration tests **31 PASS**, 2 deselected, 1 upstream deprecation warning.
- PostgreSQL integration tests **2 PASS**, 31 deselected, 1 upstream deprecation warning; includes RLS under a role without BYPASSRLS; schema migrated to head on disposable PostgreSQL 16.
- Ruff, Bandit, pip-audit, Python compile, JS syntax (node --check), Keycloak JSON parse, SBOM generation: **PASS**.
- Gitleaks **PASS** — 29 commits, ~283 KB scanned, no unignored leaks in run.
- Browser OIDC live login, token expiry/revocation, mobile E2E, 330 Bank UAT scenarios, security VA/PT, storage WORM/AV and isolated DB+blob+audit restore: **NOT RUN**.
- CI for subsequent commits must be checked independently. No locally verified runtime demo or production deployment.

## Unresolved release blockers
1. Production safety: old PoC record and audit tables lack tenant scope; app DB owner/superuser bypasses RLS. Use dedicated non-superuser NO-BYPASSRLS credentials and test tenant ACL before any real records.
2. Full records ingest with AV/MIME checks, immutable S3 originals, evidence preservation, signed JRA, effective-dated retention engine, multi-hold, dual-control destruction, fixity and DR still absent.
3. Bank IdP with MFA, provisioning/deprovisioning, secure logout/session revocation, session timeout, API canonical error format and resource-level ABAC remain incomplete.
4. Physical archive workflows, full 62 screens, OCR with human review and all reporting/integration are not done.
5. Legal and Compliance approval of current official regulation/application to Bank and all 20 TBD-BANK inputs, independent VA/PT, UAT and restore evidence are missing.

## Next controlled steps
Continue WP1 by implementing Bank-approved identity/session/RBAC hardening and non-superuser database privileges, then WP2 governance entities and approved schemes; WP3 ingest only after object storage/AV contract; WP4 deterministic retention and hold/disposal after legal JRA sign-off. Keep every unfinished menu non-clickable and every destructive operation forbidden until full release gates pass.
