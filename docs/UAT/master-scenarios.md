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
