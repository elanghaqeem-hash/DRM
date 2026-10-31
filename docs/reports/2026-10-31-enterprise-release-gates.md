# EDARMS enterprise release gates — 2026-10-31

Status: **NOT APPROVED FOR PRODUCTION**. This document defines testable gates, not evidence of implementation.

## Coverage
- 62 submenu and 414 action contracts: each must have real authorized API, persisted state, validation, error response, audit event, role-specific E2E test and Bank UAT sign-off. DESIGN_ONLY and generic-task placeholders do not pass.
- Legacy archive tables: inventory every table, FK, view, export, search index, object reference and worker; backfill tenant_id from independently validated provenance, quarantine ambiguous rows, enforce NOT NULL + composite tenant FKs and FORCE RLS, use a non-owner/non-BYPASSRLS application role. Deny unknown tenant and cross-tenant reads/writes. Never assign a guessed tenant.
- SSO/MFA: Bank-approved OIDC/SAML trust, signed issuer/audience checks, MFA claims and step-up for sensitive actions, session expiry, provisioning/deprovisioning, emergency revocation, negative replay/forgery tests. No live SSO PASS until Bank IdP test.
- Immutable: bucket versioning + object lock/compliance retention where available; verify write-once, unauthorized delete/overwrite denial, checksum and audit evidence. No WORM claim from application-level flags alone.
- Antivirus: quarantine before release, scan engine with signed updates, malware-positive and scanner-unavailable tests, fail-closed, rescan/version evidence.
- JRA: Bank-approved versioned schedule, classification mapping, retention trigger, calculation trace, authorized signatories, effective dates, exceptions. Unknown schedule = no destruction.
- Legal hold: scoped hold, approvals, notifications, immutable history, priority over JRA/disposition, no deletion until separately approved release.
- Disposition: proposed -> reviewed -> independently approved -> executed -> certificate; enforce SoD, legal hold, retention maturity, irreversible action safeguards and idempotency.
- Restore: encrypted backup, isolated restore rehearsal, RPO/RTO measurement, checksum reconciliation, tenant segregation, hold/retention preservation and signed Bank acceptance.

## Mandatory negative tests
1. Tenant A cannot access Tenant B legacy record via ID, listing, search, export, signed URL, worker or audit endpoint.
2. Database owner/superuser bypass is not used for application traffic; RLS bypass roles are explicitly denied.
3. Unmapped legacy record is quarantined, never automatically assigned.
4. Missing/expired MFA blocks sensitive approval.
5. WORM object overwrite and early deletion fail.
6. Scanner offline or positive malware detection blocks record release.
7. JRA not approved, legal hold active, immature retention or maker self-approval blocks destruction.
8. Restore preserves checksums, ACLs, legal holds, audit chain and tenant isolation.

## Release decision
CI passing existing PoC tests does **not** pass these gates. Evidence requires environment identifiers, test logs, data classification, change approval, security assessment, Bank UAT, independent model/legal review where applicable, and restore sign-off. Keep production disabled until every P0 gate passes.
