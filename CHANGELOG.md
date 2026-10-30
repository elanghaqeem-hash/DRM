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
