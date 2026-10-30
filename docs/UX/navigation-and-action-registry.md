# EDARMS navigation and action registry — WP0

**DESIGN ONLY — NO LIVE ROUTE CLAIM.** Derived from Master Prompt Bagian 4–5. There are 62 submenu and 414 explicitly named buttons. The CSV inventories action, proposed API/permission/validation/error/audit/test requirements. All controls are **NOT IMPLEMENTED** unless later verified by executable tests.

Proposed shell: accessible left collapsible sidebar, mobile drawer, role-aware navigation, active indicator, keyboard focus, 44px touch, role-scoped queries, breadcrumbs and dark/light theme. Unbuilt routes MUST be hidden or clearly disabled; no dead links or dummy KPIs.

| ID | Menu | Proposed route | Named buttons | Status |
|---|---|---|---:|---|
| A1 | Dashboard Eksekutif | `/app/a/dashboard-eksekutif` | 6 | DESIGN_ONLY |
| A2 | My Tasks & Approval Inbox | `/app/a/my-tasks-approval-inbox` | 7 | DESIGN_ONLY |
| A3 | My Records / Favorites / Recent | `/app/a/my-records-favorites-recent` | 6 | DESIGN_ONLY |
| A4 | Notification Center | `/app/a/notification-center` | 5 | DESIGN_ONLY |
| B1 | Struktur Bank & Organisasi | `/app/b/struktur-bank-organisasi` | 7 | DESIGN_ONLY |
| B2 | Archival Policy & SOP | `/app/b/archival-policy-sop` | 9 | DESIGN_ONLY |
| B3 | Kode Klasifikasi & File Plan | `/app/b/kode-klasifikasi-file-plan` | 9 | DESIGN_ONLY |
| B4 | Record Series & Types | `/app/b/record-series-types` | 7 | DESIGN_ONLY |
| B5 | Metadata Schemas | `/app/b/metadata-schemas` | 8 | DESIGN_ONLY |
| B6 | Access Classification & Regulatory Register | `/app/b/access-classification-regulatory-register` | 6 | DESIGN_ONLY |
| C1 | Kotak Masuk / Surat Masuk | `/app/c/kotak-masuk-surat-masuk` | 7 | DESIGN_ONLY |
| C2 | Surat Keluar | `/app/c/surat-keluar` | 7 | DESIGN_ONLY |
| C3 | Capture & Upload | `/app/c/capture-upload` | 8 | DESIGN_ONLY |
| C4 | QA & Record Declaration | `/app/c/qa-record-declaration` | 6 | DESIGN_ONLY |
| C5 | Digital Repository | `/app/c/digital-repository` | 9 | DESIGN_ONLY |
| C6 | Berkas / Case File | `/app/c/berkas-case-file` | 7 | DESIGN_ONLY |
| C7 | Bulk Ingest & Migrasi | `/app/c/bulk-ingest-migrasi` | 9 | DESIGN_ONLY |
| C8 | Document Templates & Controlled Drafts | `/app/c/document-templates-controlled-drafts` | 7 | DESIGN_ONLY |
| D1 | Lokasi Penyimpanan | `/app/d/lokasi-penyimpanan` | 7 | DESIGN_ONLY |
| D2 | Boks, Folder & Register Fisik | `/app/d/boks-folder-register-fisik` | 8 | DESIGN_ONLY |
| D3 | Peminjaman & Pengembalian | `/app/d/peminjaman-pengembalian` | 8 | DESIGN_ONLY |
| D4 | Stock Opname & Condition Assessment | `/app/d/stock-opname-condition-assessment` | 8 | DESIGN_ONLY |
| D5 | Transfer Fisik & Chain of Custody | `/app/d/transfer-fisik-chain-of-custody` | 7 | DESIGN_ONLY |
| E1 | Global & Advanced Search | `/app/e/global-advanced-search` | 7 | DESIGN_ONLY |
| E2 | Permintaan Dokumen | `/app/e/permintaan-dokumen` | 8 | DESIGN_ONLY |
| E3 | E-Discovery & Collections | `/app/e/e-discovery-collections` | 6 | DESIGN_ONLY |
| E4 | Akses Eksternal Terkendali | `/app/e/akses-eksternal-terkendali` | 8 | DESIGN_ONLY |
| F1 | Jadwal Retensi Arsip / JRA | `/app/f/jadwal-retensi-arsip-jra` | 8 | DESIGN_ONLY |
| F2 | Retention Calculator & Exception | `/app/f/retention-calculator-exception` | 5 | DESIGN_ONLY |
| F3 | Legal Hold Register | `/app/f/legal-hold-register` | 7 | DESIGN_ONLY |
| F4 | Appraisal & Disposal Queue | `/app/f/appraisal-disposal-queue` | 9 | DESIGN_ONLY |
| F5 | Pemusnahan & Evidence | `/app/f/pemusnahan-evidence` | 7 | DESIGN_ONLY |
| F6 | Transfer & Permanent Archive | `/app/f/transfer-permanent-archive` | 6 | DESIGN_ONLY |
| F7 | Exceptions & Permanent Records | `/app/f/exceptions-permanent-records` | 6 | DESIGN_ONLY |
| G1 | Fixity & Integrity Monitor | `/app/g/fixity-integrity-monitor` | 6 | DESIGN_ONLY |
| G2 | Preservation Plans & Format Migration | `/app/g/preservation-plans-format-migration` | 7 | DESIGN_ONLY |
| G3 | Electronic Signature & Evidence Vault | `/app/g/electronic-signature-evidence-vault` | 5 | DESIGN_ONLY |
| G4 | Backup & Restore Dashboard | `/app/g/backup-restore-dashboard` | 4 | DESIGN_ONLY |
| H1 | Audit Trail & Activity Ledger | `/app/h/audit-trail-activity-ledger` | 5 | DESIGN_ONLY |
| H2 | Compliance Control Matrix | `/app/h/compliance-control-matrix` | 7 | DESIGN_ONLY |
| H3 | PDP & Confidentiality Desk | `/app/h/pdp-confidentiality-desk` | 6 | DESIGN_ONLY |
| H4 | Operational & Regulatory Reports | `/app/h/operational-regulatory-reports` | 6 | DESIGN_ONLY |
| H5 | Risk, Incident & Follow-Up | `/app/h/risk-incident-follow-up` | 6 | DESIGN_ONLY |
| H6 | Service Level & Audit Evidence | `/app/h/service-level-audit-evidence` | 4 | DESIGN_ONLY |
| H7 | Training & SOP Center | `/app/h/training-sop-center` | 5 | DESIGN_ONLY |
| I1 | OCR Queue & Quality | `/app/i/ocr-queue-quality` | 6 | DESIGN_ONLY |
| I2 | AI Classification Review | `/app/i/ai-classification-review` | 5 | DESIGN_ONLY |
| I3 | Semantic & Assisted Search | `/app/i/semantic-assisted-search` | 5 | DESIGN_ONLY |
| I4 | Duplicate/Similarity Inspector | `/app/i/duplicate-similarity-inspector` | 5 | DESIGN_ONLY |
| I5 | AI Models & Evaluation (Admin) | `/app/i/ai-models-evaluation-admin` | 10 | DESIGN_ONLY |
| J1 | Integration Registry | `/app/j/integration-registry` | 8 | DESIGN_ONLY |
| J2 | API & Webhook Management | `/app/j/api-webhook-management` | 7 | DESIGN_ONLY |
| J3 | User & Access Administration | `/app/j/user-access-administration` | 8 | DESIGN_ONLY |
| J4 | Role & Approval Matrix | `/app/j/role-approval-matrix` | 6 | DESIGN_ONLY |
| J5 | Master Data / System Parameters | `/app/j/master-data-system-parameters` | 7 | DESIGN_ONLY |
| J6 | Workflow Builder | `/app/j/workflow-builder` | 7 | DESIGN_ONLY |
| J7 | Storage, Security & System Health | `/app/j/storage-security-system-health` | 6 | DESIGN_ONLY |
| J8 | Branding, Localization & Preferences | `/app/j/branding-localization-preferences` | 5 | DESIGN_ONLY |
| J9 | Notification Rules & Templates | `/app/j/notification-rules-templates` | 6 | DESIGN_ONLY |
| J10 | Help, Release Notes & Support | `/app/j/help-release-notes-support` | 4 | DESIGN_ONLY |
| J11 | Data Export, Portability & Exit | `/app/j/data-export-portability-exit` | 7 | DESIGN_ONLY |
| J12 | Tenant / Organization Provisioning | `/app/j/tenant-organization-provisioning` | 6 | DESIGN_ONLY |

## Release criteria
Each actual action requires route+API mapping, approved per-role+tenant policy, validation, server persistence, audit and failure state, unit/integration/E2E positive+negative tests, UI feedback and Bank UAT evidence. Only promote action status after this is observed. Common pagination/filter/save/cancel controls from Bagian 5 must be registered per screen at implementation.

See [full button registry](action-registry.csv). Existing PoC API is limited to health/audit; the new WP1 task API will cover only a subset of A2, not bulk/delegation/exports.
