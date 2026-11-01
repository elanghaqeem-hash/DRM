# Changelog — DRM

Semua perubahan penting proyek Digital Records Management dicatat dalam berkas ini. Commit GitHub adalah bukti perubahan aktual.

## [Unreleased]

### Added
- Inisialisasi repository DRM sebagai sumber kebenaran pengembangan.
- `README.md`: gambaran awal proyek, alur sinkronisasi perubahan dengan ChatGPT, status baseline, dan batasan.
- `AGENTS.md`: prosedur kerja, pengujian, keamanan, commit, dan pelaporan semua agent.
- `docs/decision-log.md`: catatan keputusan teknis untuk tata kelola pengembangan.

### Pending
- Import baseline aplikasi dan dokumen kebutuhan definitif.
- Konfirmasi stack, rancangan database, lingkungan, dan strategi deployment.
- Uji otomatis/CI, pengamanan branch, serta validasi modul secara bertahap.

### Assessment 2026-10-30
- Audit awal repository dan analisis kesenjangan Enterprise Digital Archives & Records Management disimpan di `docs/audit/2026-10-30-enterprise-drm-audit.md`.
- Ditambahkan matriks 18 kontrol, rancangan 20 modul, baseline regulasi (termasuk PADK OJK 1/2026), arsitektur target, roadmap, dan acceptance test; status aplikasi tetap `NOT VERIFIED` sampai kode dan bukti uji tersedia.

### Master prompt EDARMS — 2026-10-30
- Ditambahkan `docs/prompts/MASTER-PROMPT-EDARMS-ENTERPRISE-2026-10-30.md` sebagai prompt eksekusi enterprise end-to-end dengan 10 grup menu, 62 submenu, kontrak field/form/tombol, lifecycle, JRA, legal hold, disposisi, physical custody, UI/UX, keamanan, AI/OCR, API, 330 skenario UAT rancangan, serta WP0–WP9.
- Dokumen adalah spesifikasi/prompt pengembangan; tidak menyatakan aplikasi, tes, atau deployment telah selesai.


### PoC implementation history retained from feature/sprint0-foundation


## [Unreleased] — 30 October 2026
### Added
- Imported PoC Sprint 0 API, PostgreSQL migration, OIDC authentication, audit hash chain,
  Docker Compose, migration workflow, tests, and CI configuration.
- Open Bank parameter register, provisional traceability and release gates.
- Sprint 1 control-driven pure record domain policies: classification approval,
  maker-checker, mandatory metadata and immutable record statuses.
### Known gaps
- No end-to-end UAT, PostgreSQL smoke test in this execution environment,
  production WORM, ABAC, KMS/HSM, or Bank-approved settings.
- Referenced source proposal PDF has not yet been reconciled.
- Final XLSX compliance matrix is not yet committed in this initial code import.
### Prior history
- Repository and AGENTS.md initialized as shared source of truth.


### EDARMS WP0 / WP1 (2026-10-30)
- Imported current EDARMS master prompt and enterprise audit from main to PoC-based working branch without deleting existing FastAPI code.
- Added verified audit baseline, draft BRD, VERIFY control matrix, conceptual ERD, 10 group/62 submenu navigation catalog, 414-action registry and 330 planned UAT slots (NOT RUN).
- Added migration 0002 tenant-scoped generic review tasks, membership, task history and FORCE RLS; implemented authorized inbox/create/decide API with idempotency, SoD and optimistic concurrency.
- Added domain and PostgreSQL integration tests; corrected Gitleaks checkout history issue. CI result must be observed before treating gate as PASS.
- Not done: UI/UX routes and 62 working screens, Bank IAM/MFA, tenant retrofit of legacy record/audit, AV/object storage, Bank JRA/legal hold/disposal, production and restore drill.
- Bank parameters remain TBD-BANK / VERIFY, WP0 Bank approval PENDING.


### WP1 browser workspace and CI gates — 30 October 2026
- Added `/app` FastAPI-served responsive PoC UI with accessible collapsible sidebar, real tenant-scoped generic task operations and PKCE Keycloak test client.
- Extended CI to validate JS syntax and JSON realm; added UI smoke tests. On GitHub Actions run 41031409696: 31 unit/non-integration tests PASS, 2 PostgreSQL integration tests PASS, Ruff/Bandit/SCA/SBOM/Gitleaks PASS.
- Gitleaks reviewed false-positive fingerprint is tightly documented; real credentials still prohibited. RLS validated using non-BYPASSRLS read role; actual PoC owner superuser remains a production gate.
- Added WP0/WP1 evidence and open-blocker report. Full Bank IdP, secure server logout, 62 menu actions, 330 UAT execution, AV/WORM/DR/retention engine, and production are NOT COMPLETE.

### EDARMS P0 tenant isolation and security adapters — 2026-10-31
- Migration 0003: tenant quarantine and FORCE RLS over 24 legacy tables, tenant-aware composite FKs; no historical tenant guessed.
- Separate NOLOGIN/NOBYPASSRLS runtime grants and provisioned API login, Compose API credential separation, role-aware readiness, tenant-scoped audit chain.
- Signed-token MFA assurance and recent auth_time checks for sensitive decisions; staging requires Bank-provided accepted claims.
- ClamAV INSTREAM and S3 Object Lock COMPLIANCE adapters with fail-closed negative tests; synthetic unit tests only, no live Bank services.
- Added migration/backfill count report, P0 execution report and CI integration RLS tests with runtime login.
- **Still pending:** Bank tenant provenance backfill, IdP federation, real scanner/object-lock integration UAT, external audit WORM anchor, approved JRA, 62 functional submenu release and production gates.

### EDARMS production readiness roadmap — 2026-10-31
- Added `docs/roadmap/EDARMS-PRODUCTION-READINESS-2026-10-31.md`: prioritized WP00–WP09, 62 submenu/414 action coverage, Bank-controlled go-live gates, tenant/SSO/AV/WORM/JRA/hold/disposition/restore requirements, UAT journeys, proposed schedule and responsibility matrix.
- Roadmap is advisory only; does not activate production, approve Bank JRA, merge PRs, or demonstrate UAT/infrastructure readiness.

### EDARMS WP00–WP04 critical path, controlled draft and restore — 2026-11-01
- Implemented tenant RLS-controlled JRA evidence registry (application read-only), independent legal hold apply/release and immutable hold events, deterministic retention appraisal, multi-actor proposal/review/approval for disposition with **destruction and external object deletion still prohibited**.
- Alembic 0004 protects original versions and legacy statuses; Alembic 0005 adds DB-enforced approved classification + mandatory metadata for DRAFT-only record creation and append-only evidence.
- Exposed scoped API for approved classes, DRAFT records, retention preview, legal holds and disposition review; sensitive transitions include configurable MFA assurance checks.
- Added synthetic unit/integration tests for multi-hold, tenant boundary, policy, maker-checker and actual isolated pg_dump/pg_restore. Verification counts and latest CI run are tracked in PR #4.
- Added CLI production evidence gate for 62 submenu/414 actions. **No action has Bank UAT PASS** merely by adding its design entry.
- Production: **NO-GO**. Bank-approved tenancy migration, SSO/MFA, AV/KMS/WORM, operational JRA/signatures, original capture, independent VA/PT, Bank DR/restore and all 62/414 E2E remain pending. PR #3 has divergent migration history; reconcile before merge.
