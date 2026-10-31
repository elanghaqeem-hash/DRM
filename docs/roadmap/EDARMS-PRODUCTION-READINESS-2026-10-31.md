# EDARMS Enterprise — Production Readiness Roadmap
**Versi:** 1.0 | **Tanggal:** 31 Oktober 2026 | **Status:** RECOMMENDATION / NOT IMPLEMENTED
**Repository:** https://github.com/elanghaqeem-hash/DRM
**Branch kerja saat rekomendasi:** feature/edarms-wp0-wp1-20261030
**Tujuan:** Bank-operational end-to-end digital, physical, and hybrid records management, 62 submenu, 414 registered actions.

> Dokumen ini adalah rencana pengembangan, bukan sertifikat kesiapan produksi, hasil UAT, atau bukti telah dilakukan deployment. Semua keputusan Bank harus memperoleh persetujuan yang sesuai.

## 1. Verified technical baseline
- Stack yang dipertahankan: Python/FastAPI, PostgreSQL 16, Alembic, Keycloak/OIDC, Redis, S3-compatible MinIO/Object Lock adapter, ClamAV adapter, Docker Compose PoC.
- 10 grup A–J, 62 submenu, 414 aksi sesuai `docs/UX/navigation-and-action-registry.md` dan `docs/UX/action-registry.csv`; 411 aksi `DESIGN_ONLY`, tiga aksi tugas generik PoC. Tidak ada bukti 62 submenu production-ready.
- Alembic 0003: `tenant_id`, FORCE RLS, tenant-composite FK untuk 24 tabel legacy, quarantined unknown legacy ownership; sebagian constraint `NOT VALID` dan backfill bank provenance belum dilakukan.
- App runtime role non-superuser/NOBYPASSRLS telah disiapkan, perlu bukti runtime environment nyata; hash chain audit, signed token OIDC, recent MFA claim enforcement di sejumlah endpoint sensitif.
- ClamAV INSTREAM + S3 Object Lock adapters diuji menggunakan fake socket/store, bukan scanner dan WORM Bank yang sesungguhnya; belum terpasang dalam proses ingestion arsip end-to-end.
- Konfigurasi produksi masih diblokir secara sengaja di settings. Seluruh Bank-specific parameters dari `docs/open-parameters.md` belum disahkan.
- PR #2 telah berstatus non-Draft namun belum merged saat baseline; status PR dan CI harus dicek lagi saat release.

## 2. Required decision principles
1. **No silent success:** setiap aksi memiliki respons, perubahan data, bukti audit dan negative test, bukan sekadar halaman.
2. **Deny by default:** record atau tenant tidak teridentifikasi → quarantine; aturan retensi tanpa persetujuan → blokir disposisi; scanner unavailable → blokir rilis.
3. **Record integrity:** draft boleh direvisi secara terkontrol; declared originals harus immutable, koreksi membuat versi terhubung. Metadata, provenance, checksum dan chain of custody wajib tersimpan.
4. **Legal hold is orthogonal:** satu record dapat memiliki beberapa hold; release satu hold tidak membuatnya layak dimusnahkan jika hold lain masih aktif. Hold mengalahkan JRA.
5. **Least privilege and dual control:** no self approval untuk deklarasi sensitif, legal hold release, dan disposisi; privileged support tidak otomatis dapat membaca konten nasabah.
6. **Retain existing services:** upgrade FastAPI/PostgreSQL secara incremental; jangan rewrite besar tanpa demonstrasi business case, migration, regression.
7. **Compliance is evidence-based:** regulasi diverifikasi Legal/Compliance per pasal, tanggal efektif, ruang lingkup Bank; standar ISO adalah design reference bukan klaim sertifikasi.

## 3. Work packages and dependencies
| WP | Prioritas | Lingkup implementasi | Bukti keluar / exit gate | Dependensi |
|---|---|---|---|---|
| WP00 | P0 | Discovery, Bank sign-off BRD, arsitektur, data classification, approved file plan/JRA, RACI, 62x414 traceability, threat model, risk register, cloud/DC-DRC decision | signed BRD, approved parameters, regulatory/control mapping | Bank SME |
| WP01 | P0 | Runtime tenant isolation, provenance backfill, validate tenant FKs/NOT VALID, least-privilege DB; SSO/MFA, SCIM/JIT, role & ABAC, revocation, secrets/KMS, network segmentation, isolated dev/UAT/prod | automated tenant matrices, IdP end-to-end, security sign-off | WP00 |
| WP02 | P0 | Organization/file plan, taxonomy/record series, controlled metadata, classifications, policy effective dates, maker-checker & four-eyes workflows, event ledger | Bank-approved taxonomy + positive/negative workflow UAT | WP00–01 |
| WP03 | P0 | API+UI capture incoming/outgoing/digital, antivirus quarantine, MIME/content inspection, OCR QA, QA declaration, immutable WORM with signed inventory, search indexing | file lifecycle + fail-closed scans + actual object-lock tests, no real Bank data before sign-off | WP01–02 |
| WP04 | P0 | Effective-dated JRA, trigger calculator, conflicting-rule/exception priority, multiple legal holds, appraisal, disposition & permanent transfer with independent authorization and evidence | documented decision trace + impossible premature destruction + signed evidence | WP02–03 |
| WP05 | P1 | Physical locations, barcode/QR, containerization, loans/returns, movement & chain of custody, stock opname, asset condition | complete physical custody UAT and inventory reconciliation | WP02 |
| WP06 | P0/P1 | ACL-aware index/search, request/disclosure, preview watermark, external access/e-discovery, PDP requests/ROPA/DPIA, export redaction | cross-tenant no leak via counts/snippets/previews/export; legal/DPO approval | WP01–04 |
| WP07 | P0 | Fixity, preservation plans, format migration, audit WORM anchor independent from DBA, backup/restore, security/SIEM observability, compliance & operational reporting | integrity proofs, DR rehearsal, report reconciliation & SoD evidence | WP01–06 |
| WP08 | P1 | Integration registry/API/webhooks/queues, legacy source migration connectors, workflow builder, notification rules, admin, AI/OCR assisted suggestions with HITL, portability/exit | replay-safe integration, integration contract tests, model evaluation and export+reimport | WP01–07 |
| WP09 | P0 | Complete UX and action coverage, UAT per role, regression/performance/accessibility/VA-PT, pilot, cutover, rollback, training, handover and hypercare | 62/414 traceability, independent sign-off and formal go/no-go | all |

**Implementation sequencing:** WP00/WP01 run first; WP02→WP03/WP04 underpin true record lifecycle; physical and search can proceed in parallel after the core; WP09 is a release gate, not a substitute for earlier testing.

## 4. Coverage management for all 62 submenu
| Group | Submenu | Gate focus | Suggested release wave |
|---|---:|---|---|
| A. Workspace & Dashboard | 4 | real metrics, task delegation/inbox, favorites, notifications | 1–2 |
| B. Governance & Metadata | 6 | Bank-owned file plan, classification, schema version, policy/effective dates | 1 |
| C. Capture & Digital Records | 8 | complete receive/upload/QA/declare/version/bulk ingest & controlled drafts | 1–2 |
| D. Physical Archive | 5 | barcode, custody, loan, stock opname, physical transfer | 2 |
| E. Search & Access | 4 | ACL/tenant-aware indexing, requests, external disclosure & e-discovery | 1–2 |
| F. Retention & Legal | 7 | approved JRA, hold, multi-approval disposal, evidence, permanent archive | 1–2 |
| G. Preservation | 4 | checksum, preservation, signed evidence, restore | 1–2 |
| H. Audit & Compliance | 7 | audit integrity, PDP, regulatory reports, risk, SLA, training | 1–3 |
| I. AI & OCR | 5 | human-approved suggestions, privacy, drift, accuracy, ability to disable | 3 |
| J. Administration & Integration | 12 | IAM, tenant provisioning, rules, integrations, portability & system health | 1–3 |
| **TOTAL** | **62** | **414 registered actions must be fully traced** | **Enterprise production = waves 1–3 passed** |

Wave 1 dapat dipakai sebagai pilot terbatas hanya bila semua fungsi yang diaktifkan beserta gate P0-nya lolos dan Bank menyetujui pembatasan; **Wave 1 bukan klaim bahwa 62 submenu selesai**.

Each button's Definition of Done:
- displayed for authorized roles only; keyboard accessible; has correct loading/empty/error/success state;
- real route + versioned OpenAPI contract and validated request/response;
- server-side tenant/resource RBAC+ABAC, independent approval/SoD and immutable audit;
- persisted ACID transaction or durable idempotent async job; concurrency and retries handled;
- 1 positive, 1 negative, 1 unauthorized, 1 cross-tenant test where relevant, plus edge/cancel/duplicate tests;
- CI integration test, browser E2E, Bank UAT record and signed evidence; status only changes from DESIGN_ONLY with evidence;
- searchable/exportable objects, cache, queue jobs, temporary URLs and audit endpoint follow the same tenant ACL.

## 5. Architecture hardening — must not be deferred
### Tenant and data isolation
- Reconcile historical ownership with signed source-system provenance. Use controlled migration batches, immutable mapping ledger, counts/hash reconciliation; never infer tenant from document title or arbitrary joins.
- Complete validation of `NOT VALID` legacy FK/check constraints after reconciliation. Use explicit tenant-aware constraints on links, object pointers, queues and search indexes.
- Runtime role must be non-owner, non-superuser, NOBYPASSRLS; deny direct DB access by end users. Use transaction-scoped tenant context with strictly authenticated actor, not a client-supplied arbitrary tenant alone; consider SQL injection as tenant-context spoofing attack.
- Negative tests across APIs, direct ID, list/search counts/snippets, OCR jobs, previews, exports, signed URLs, logs, caches, background jobs, admin and restore, concurrent tenant switches.
- Verify append-only audit hash chains remain verifiable per tenant, with independent WORM anchors and restricted verification privilege.

### Bank identity / cryptography
- Bank-approved OIDC/SAML federation, PKCE where appropriate, issuer/audience/nonce/time checking, MFA assurance ACR/AMR, stepped-up auth for sensitive operations; session expiry, account disabling, emergency revocation, device policy.
- SCIM or equivalent lifecycle joiner/mover/leaver, periodic access review, delegated admin scope and segregated break-glass procedure with monitoring.
- TLS, mTLS for machine interfaces as selected by Bank, KMS/HSM and envelope encryption, key rotation, secrets vault, independent custody, DB encryption and backups, no sensitive contents in logs or external AI.

### Archive content / immutable storage
- Quarantine all incoming content until size/type/MIME and decompression safety checks plus actual AV verdict complete. Positive malware/unavailable scanner **must block** downstream searchable/published data; allow secure retry/rescan.
- Approved S3 Object Lock Compliance/retention with bucket versioning and demonstrable delete/overwrite denial, SHA-256 verified receipt and fixity sampling; no compliance claim from application attributes alone.
- WORM retention deadline must reconcile with JRA and legal hold, and block disposition while storage retention protection remains; avoid prematurely locking records with unapproved or guessed retention periods.
- Record states: DRAFT → QUARANTINED → QA_PENDING → DECLARED → ACTIVE/INACTIVE → ELIGIBLE → REVIEWING → DISPOSED/TRANSFERRED. **HOLD is a parallel constraint**, not a single mutually exclusive status.
- Explicitly link source content, rendition, OCR text, derivatives, signatures and document versions; all exports preserve provenance.

### Business process safety
- JRA only from signed, versioned and effective Bank schedule; preserve rule version and trigger evidence per calculation. No default universal retention duration; unknown rule blocks destruction.
- Disposition requires proposal, multi-stage independent approvals, legal/hold/retention recheck immediately before execute, idempotent execution, certificate and defensible evidence.
- Legal hold: both record and query/series scopes, immutable case event history, future-matching records captured according to approved policy, distinct hold release approvals.
- PDP workflows reconcile data-subject rights with mandatory statutory retention and lawful hold; require Legal/DPO decision rather than automatic deletion.

## 6. End-to-end mandatory UAT journeys
J1 Bank SSO+MFA → role scoped workspace → logout/revocation.
J2 Receive or digitize → quarantine/AV → OCR → metadata QA → classification → declaration → WORM version → search.
J3 Draft → amendments/version links → approval → immutable original preserved.
J4 Record request → authorized preview → redacted release/export → auditable chain of custody.
J5 Event-triggered JRA → retention calculation → hold check → review → signed disposition certificate.
J6 Multiple legal holds → partial release → disposal still prohibited → final authorized release.
J7 Barcoded physical accession → shelf/box → loan → overdue → return → stock reconciliation.
J8 Legacy migration → provenance mapping → quarantine unresolved → per-tenant checksum/count reconciliation.
J9 Malicious upload/scanner-down → never published or searchable → incident response evidence.
J10 Tenant A to Tenant B ID/search/export/object URL/worker/log access attempts → denied.
J11 Full DB+object+audit backup → isolated recovery → restore of ACL/hold/metadata/hash chain → measured RPO/RTO.
J12 Exit/portability → authorized BagIt-like package + metadata + SHA-256 manifest + reimport validation.
J13 PDP rights request → lawful-basis/hold review → redacted decision and audit.
J14 Operational monitoring → alert escalation/SOC → backup review/incident handling and tested support process.
J15 AI suggestion → human override/correction → no autonomous delete, approval or data transfer.

## 7. Testing and non-functional acceptance
Minimum planned suites:
- 414 action-level positive/negative tests; 62 screen browser tests; role matrix (creator, officer, manager, legal, compliance, DPO, approver, auditor, IT, tenant admin, service), and cross-tenant tests.
- Contract/API and integration testing with actual Postgres/runtime role, actual Bank IdP in UAT, actual AV and WORM target, malicious fixture tests, interrupted uploads, storage unavailable and network failure.
- DAST/SAST/SCA/SBOM, secrets scanning, security configuration checks, independent penetration testing, tenant IDOR/BOLA, CSRF/XSS/SSRF, malicious document, session fixation, object URL reuse, audit corruption and concurrency/race.
- Load testing against **Bank-approved** volume profile; query pagination, indexing, OCR async capacity, error budget, query/cache isolation.
- WCAG 2.2 AA target, Bahasa Indonesia UX, desktop/mobile, keyboard and accessibility, real user pilot.
- DR: offsite encrypted backups, test DB + objects + index + audit anchors, signed restore report, step-by-step rollback plan.

**Proposed NFR for Bank review, NOT regulatory promises:** 99.9% service availability per month; p95 interactive list/search ≤2s at agreed load; RPO ≤15 minutes and RTO ≤4 hours for priority services, subject to Bank BIA and feasibility; target 100% passing P0 controls and 0 unresolved Critical/High vulnerabilities before release. Record agreed baselines, measurement windows, exclusions and owner approval.

## 8. 10 mandatory go-live gates
G1 Bank BRD/SOP/records taxonomy and 20+ open parameters signed.
G2 Legislative mapping, JRA, disposal authority, PDP/legal exception approved.
G3 Every one of 62 submenu / 414 action requirements implemented/tested and UAT signed for enterprise general availability.
G4 Legacy tenant data provenance reconciled, NULL quarantines dispositioned, constraints validated; no cross-tenant leakage in any path.
G5 Real Bank SSO/MFA, role/ABAC and revocation end-to-end negative UAT passed.
G6 Real malware/AV and immutable object lock integration with delete/overwrite failure evidence.
G7 JRA/hold/disposition dual controls, independent approval and immutable evidence UAT passed.
G8 Independent SAST/DAST/VA/PT; Critical/High=0 unresolved; risk acceptance and residual risk registry signed.
G9 Backup + restore and DR rehearsal evidence including RPO/RTO, tenant boundaries and data integrity.
G10 Change advisory, runbooks, owner RACI, data migration sign-off, cutover/rollback, monitoring/SOC, training, Bank final go/no-go and pilot acceptance.

**Release rule:** No live Bank archive data until G1/G2/G4/G5/G6/G8/G9 for the in-scope pilot pass. Full enterprise operational completion requires G1–G10 including 62/414. Documentation-only/CI mock PASS does not fulfill external gates.

## 9. Suggested execution schedule and responsibilities
An indicative 28–36 week plan from fully approved requirements and timely Bank integration access; this is a planning estimate, not a delivery commitment.

| Window | Work and milestone |
|---|---|
| W01–W03 | WP00 discovery, sign-off, traceability, threat model, Bank infrastructure decision |
| W03–W08 | WP01 tenant reconciliation, Bank identity and real storage/AV pilot integrations |
| W06–W13 | WP02 metadata/classification and WP03 secure ingest/declared record lifecycle |
| W10–W18 | WP04 JRA/legal hold/disposal and WP05 physical custody |
| W14–W23 | WP06 search/access and WP07 audit/preservation/restore |
| W19–W27 | WP08 integrations, AI/OCR and long-tail J/admin actions |
| W23–W34 | WP09 62/414 coverage closure, E2E UAT, VA/PT, performance/DR, pilot and cutover |
| W34–W36 | Bank-approved go-live, limited hypercare, release evidence and transition to operations |

**Bank owners:** Business/Records sponsor, Legal, Compliance, DPO, InfoSec/CISO, IAM, IT Ops/DBA, BCP/DR, Risk, Internal Audit independent assurance and source system custodians.
**Delivery roles:** Product Owner, solution/security architects, backend+frontend, DBA/data engineer, QA automation, DevSecOps/SRE, integration engineer and records/legal SME.
**Governance:** weekly risk/blocker review; fortnightly demonstration; every WP closes with commit SHA, PR, CI evidence, database migration dry run, traceability, release notes and Bank acceptance.

## 10. Operations and cutover
- Separate isolated dev/UAT/pre-prod/prod, no copy of real Bank archives into open PoC; Bank-approved hosting/data residency and backups.
- CI/CD with signed artifacts, protected main/review rules, reproducible images, protected secrets, migration backups, feature flags, observability and rollback; no ad hoc live edits.
- Dry-run migration with test population, hash/count reconciliation, old-system read-only window, cutover runbook, rollback point, exception handling and signed owner decision.
- SRE/Operations: 24/7 incident escalation according to contract, SOC integration, vulnerability management, backup verification, certificate expiry, capacity, service desk, SLA dashboard, runbooks and access recertification.
- Pilot two controlled departments with real Bank approval; expand by institution/unit only on verified guardrails, recheck tenant and entitlement matrices.

## 11. Regulatory verification checklist (Legal & Compliance must sign applicability)
- UU 43/2009 Kearsipan and PP 28/2012; UU 8/1997 Dokumen Perusahaan; PERANRI 6/2021 Pengelolaan Arsip Elektronik (confirm BUMD/BPD applicability and current amendments).
- UU 27/2022 PDP; UU ITE with amendments and PP 71/2019 for electronic evidence/system integrity.
- POJK 11/POJK.03/2022, PADK OJK 1/2026 **effective 1 March 2026** (Bank Umum TI implementation), SEOJK 29/SEOJK.03/2022 cyber resilience; verify scope, amendments, reporting and Bank applicability before encoding as executable rules.
- Reference frameworks: ISO 15489, ISO 16175, ISO 23081, ISO 27001, ISO 22301, OWASP ASVS, WCAG 2.2 AA. Design reference, not automatic certification.

Official starting references:
- https://ojk.go.id/id/regulasi/Pages/PADK-1-Tahun-2026-Penyelenggaraan-Teknologi-Informasi-oleh-Bank-Umum.aspx
- https://ojk.go.id/id/regulasi/Pages/Ketahanan-dan-Keamanan-Siber-Bagi-Bank-Umum.aspx
- https://jdih.anri.go.id/index.php/peraturan/peraturan-arsip-nasional-republik-indonesia-no-6-tahun-2021
- https://peraturan.bpk.go.id/Details/38788/uu-no-43-tahun-2009
- https://peraturan.bpk.go.id/Details/229798/uu-no-27-

## 12. Next concrete engineering tickets — first 14 days (conditional on access)
1. Compare current branch to main, close/retire overlapping PR, preserve passing CI and keep PR guarded until Bank gate.
2. Build gap dashboard generating 62/414 status from `action-registry.csv` and actual route/test coverage; ban manual unsupported COMPLETE flags.
3. Produce legacy 24-table provenance inventory + reconciliation tool and formal mapping review, with no automatic tenant guessing.
4. Validate existing `NOT VALID` constraints on migrated test data, add invariant tests for all cross-tenant FK/view/index/queue/object URLs.
5. Integrate a disposable actual ClamAV service and actual locked S3-compatible test bucket; capture failure proofs and receipts.
6. Bank IAM integration contract: issuer/audience/acr/amr provisioning, session revocation, role matrix, browser E2E.
7. Implement first vertical slice: intake → quarantine → QA → declaration → immutable version → authenticated search.
8. Create approved JRA template and signed policy import workflow; never seed fabricated Bank retention periods.
9. Add signed evidence manifest and independent auditor checklist for each release gate.
10. Publish detailed sprint backlog with owners/dependencies, UAT scripts and evidence retention path.

**Current release decision: NOT READY FOR PRODUCTION. No deployment, approval or live Bank integration was performed by writing this roadmap.**
