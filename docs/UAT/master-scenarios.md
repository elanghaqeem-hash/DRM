# EDARMS UAT master — WP0 coverage skeleton

**PLANNED, NOT EXECUTED.** Master Prompt Bagian 12 defines 330 intended scenario slots. This file is a tracking skeleton, not 330 authored or passed tests.

| IDs | Scope | Count | Current state |
|---|---|---:|---|
| UAT-001–040 | Governance/metadata/policy | 40 | DESIGN_REQUIRED |
| UAT-041–100 | Ingest, QA, repository/search | 60 | DESIGN_REQUIRED |
| UAT-101–145 | Physical, custody, loans | 45 | DESIGN_REQUIRED |
| UAT-146–205 | Retention, holds, disposal | 60 | DESIGN_REQUIRED |
| UAT-206–245 | Fixity, evidence, restore | 40 | DESIGN_REQUIRED |
| UAT-246–290 | Privacy, RBAC, audit, reporting | 45 | DESIGN_REQUIRED |
| UAT-291–330 | OCR, integration, mobile | 40 | DESIGN_REQUIRED |

## Adversarial gate — all NOT RUN
- P0-ADV-01 Self-approval blocked — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-02 Remaining active legal hold blocks destruction — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-03 Hold arriving during execution aborts destruction — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-04 Cross-tenant forged record ID denied — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-05 Search facets do not leak unauthorized counts — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-06 Platform admin cannot modify sealed evidence — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-07 MIME spoof/zip bomb quarantine — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-08 Stale update yields conflict — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-09 Expired external share denies — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-10 OCR prompt injection cannot bypass policy — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-11 Permanent record never disposed — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-12 Missing retention trigger blocks disposal — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-13 Restore hash mismatch escalates — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-14 Corrupt blob triggers fixity incident — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-15 Bulk failure reconciles — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-16 PDF/Office viewer never executes scripts — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-17 CSV formula injection neutralized — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-18 Logs do not leak secrets — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-19 Duplicate webhook is idempotent — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.
- P0-ADV-20 Mobile sidebar/keyboard/logout are accessible — pending test data, steps, UI/API/DB/audit assertion, evidence, sign-off; NOT RUN.

For every scenario: test ID, priority, precondition, role, synthetic fixture, steps, expected UI/API/DB/audit, evidence path, result, defect, retest and Bank approver required. No default Bank retention fixture. See specific tests as they are built.


## 2026-10-31 automated PoC evidence (not Bank UAT sign-off)

These tests exercise **synthetic** fixtures only; their pass/fail must be verified from the corresponding GitHub CI run. None substitutes for the 330 Bank UAT scenarios:

| File | Critical assertions | Classification |
|---|---|---|
| `tests/integration/test_archive_isolation.py` | 18-table tenant RLS; cross-tenant FK; immutable versions and declared records | Automated PostgreSQL |
| `tests/integration/test_legal_hold_retention.py` | Actual restricted DB runtime role, apply 2 holds, independent release, other hold continues blocking | Automated PostgreSQL |
| `tests/unit/test_retention_eligibility.py` | Trigger missing, JRA missing, permanent, dynamic/multi-hold, never authorize destruction | Domain unit |
| `tests/unit/test_bank_mfa.py` | Required signed OIDC ACR mismatch denies, no implied Bank IdP UAT | Auth unit |
| `tests/unit/test_secure_ingest.py` | AV fail, MIME spoof, missing S3 COMPLIANCE lock, checksum mismatch deny | Fake-adapter unit, not real AV/S3 |
| `tests/unit/test_restore_manifest.py` | Manifest DB/object/audit completeness, tamper and traversal failures | File manifest unit, not DR rehearsal |
| `tests/unit/test_archive_api_auth.py` | Anonymous archive/legal API denies | HTTP contract unit |
| `tests/unit/test_menu_registry.py` | 62 submenu/414 action inventory, no fake production DONE labels | Inventory integrity, not feature E2E |

**Unexecuted release-critical testing:** live Bank IdP/MFA and logout/revocation, actual antivirus signatures, WORM object retention/readback and KMS rotation, signed Bank JRA, independent disposal dual approval and race tests, complete UI Playwright/Android, cross-role 330 UAT, full database/object/audit isolated restore, VA/PT, performance, accessibility and regulatory sign-off.
