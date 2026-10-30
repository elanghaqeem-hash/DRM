# EDARMS Business Requirements — WP0 Draft

**Status: DRAFT / BANK APPROVAL PENDING.** Source: master prompt dated 2026-10-30, existing enterprise audit, PoC PR #1. No Bank policy, JRA, classification, legal interpretation, or production approval is implied.

## Product boundary and users
Enterprise records platform for physical, digital-native, digitized and hybrid files. Govern creation, capture, quarantine, quality control, immutable declaration, access, retention trigger, multi-scope legal hold, appraisal, signed disposal, transfers, preservation, and authorized export. This is NOT an ordinary DMS/file sharing system.

Personas: employee creator/requester, unit owner, records operator, records manager, distinct reviewer/checker, approver, Legal, Compliance, DPO, Internal Audit, External Auditor/Regulator, IT/Security, Management, Bank Admin, System Admin (no blanket content access), machine client. Actual role bindings and RACI require Bank approval.

## Functional and non-functional requirements
| FR Group | Required observable outcome | WP | Gate |
|---|---|---|---|
| A | Role-scoped dashboard and real task inbox | 1 / 8 | No fake KPI, no self-approval |
| B | Org, file plan, series, policy and versioned metadata | 2 | Bank-approved taxonomy and rule owners |
| C | Correspondence, controlled ingest, AV, QA, immutable originals | 3 | SHA-256, provenance, malware quarantine, SoD |
| D | Physical locations, barcode, loan, transfer and chain of custody | 5 | Custodian acknowledgements and audit |
| E | Global ACL-aware search, requests, disclosure, e-discovery | 5–6 | Cross-tenant counts, previews and exports never leak |
| F | JRA triggers, exceptions, independent holds and disposal | 4 | No auto-destruction, dual human approval, recheck |
| G | Fixity, format preservation, evidence package, restore | 6 / 8 | Independent restore/checksum evidence |
| H | Immutable audit, PDP, legal control and regulatory report | 6 | Control owner/legal signoff |
| I | OCR and AI recommendations with human approval | 7 | Evaluation metrics and human overrides |
| J | Identity, tenant policy, admin, integrations, portability | 1 / 7–8 | Deny-by-default and verified exit export |

Full 62 submenu and 414 named button design inventory: [Navigation](../UX/navigation-and-action-registry.md). These are **requirements**, not implemented features.

## Record lifecycle invariants
- Working drafts may be edited with optimistic concurrency and audit; declared originals must remain content-immutable. New corrections require linked versions and provenance.
- Classification and metadata rules must be approved and effective-dated; no inferred Bank values.
- Retention eligibility needs event trigger and approved JRA version, conflict check, legal basis and hold review. If unknown, BLOCK.
- Any active scoped legal hold blocks disposal. Releasing one of several holds never frees the record.
- Destruction requires maker-checker separation, two independently authorized signoffs, just-in-time re-evaluation and signed certificate; AI cannot approve or delete.
- Audit, preview, search, export, background workers, object store and tenant boundaries must all recheck authorization.

## NFR acceptance
| NFR | Requirement | Threshold/owner |
|---|---|---|
| Security | Signed OIDC token, Bank MFA, scoped RBAC+ABAC, KMS, safe upload, negative tests | TBD-BANK |
| Integrity | Original hashes, out-of-band WORM audit anchors, controlled versioning | Bank evidence required |
| Resilience | Backup database + blobs + audit, tested isolated restore | RPO/RTO TBD-BANK |
| Usability | WCAG 2.2 AA, accessible keyboard/focus, left collapsible sidebar, Android 360px | E2E evidence pending |
| Scalability | API pagination, indexes, job queue, benchmark with synthetic volume | Volume/SLA TBD-BANK |
| Interoperability | Versioned OpenAPI, export metadata+hash+provenance | Owners TBD-BANK |
| Privacy | No sensitive document text/secrets in logs or external AI | DPO/Legal approval |

## Proposed RACI — not Bank-approved
| Action | Responsible | Accountable | Consulted/Checker |
|---|---|---|---|
| Intake/metadata | Unit Creator + Records Officer | Unit Owner | Records Manager |
| Publish JRA | Records Manager | Bank archival authority | Legal + independent approver |
| Legal hold/release | Legal Officer | Legal Head | Independent hold-release reviewer |
| Disposal | Records Unit | Bank-authorized records authority | 2 independent approvers, Legal |
| Restore | IT DR Operator | IT Head | IT Security + Internal Audit |

## Threat model summary
P0 threats: tenant IDOR/BOLA; role spoofing and self-approval; malicious Office/PDF/OCR; MIME spoof/zip bombs; CSRF/XSS/SSRF; presigned object URLs; retention/hold race; privileged DB audit tamper; data in logs; backup mismatch; CSV formula execution. Bank SOC/security review required. See [UAT skeleton](../UAT/master-scenarios.md).

## Open approvals
All **TBD-BANK-001 through TBD-BANK-020** from Master Bagian 15 remain open: institution applicability, organization hierarchy, taxonomy, JRA/trigger, permanent series, disposal authority, confidentiality, IdP/MFA, SoD, object storage/KMS, hosting, restore RPO/RTO, volume, source systems, AI/data residency, privacy procedures, signatories and production release. WP0 cannot pass organizational sign-off without these.
