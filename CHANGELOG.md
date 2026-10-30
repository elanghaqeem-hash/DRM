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
