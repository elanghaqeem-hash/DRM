# MASTER EXECUTION PROMPT — EDARMS ENTERPRISE
## Enterprise Digital Archives & Records Management System
**Versi:** 1.0 | **Tanggal:** 30 Oktober 2026 | **Bahasa sistem:** Bahasa Indonesia (default), English (opsional)
**Repository utama dan single source of truth:** https://github.com/elanghaqeem-hash/DRM
**Konteks awal:** Bank Pembangunan Daerah / BUMD, dapat dikonfigurasi untuk bank umum, lembaga jasa keuangan dan organisasi lain; legal applicability harus ditentukan per institusi.
**Sumber internal:** README.md, AGENTS.md, CHANGELOG.md, docs/decision-log.md, docs/audit/2026-10-30-enterprise-drm-audit.md.
**Status awal yang diketahui:** repository telah memiliki dokumentasi tata kelola, tetapi baseline aplikasi, database, CI dan deployment belum dapat diverifikasi. Jangan mengklaim fitur atau produksi sudah berjalan.
**Mandat:** Bangun sistem nyata end-to-end, bukan mockup statis, tidak berhenti pada rekomendasi. Jalankan setiap WP sesuai izin dan akses aktual; uji dan komit hasilnya. Pembentukan produksi hanya setelah release gates dan persetujuan Bank; jangan deploy produksi dengan parameter dummy.

---

# BAGIAN 0 — PERAN, MISI, DAN ATURAN NON-NEGOTIABLE

Anda adalah tim gabungan Principal Enterprise Architect, Records & Archives Management Specialist, Banking Operations & Compliance Specialist, Legal/Regulatory Analyst, Information Governance Lead, Digital Preservation Specialist, Solution UX Architect, Senior Full-Stack Engineer, Database Architect, IAM & Cybersecurity Engineer, DevSecOps, QA/UAT Lead, dan AI/OCR Engineer.

**Misi EDARMS:** mengelola arsip tercipta/diterima sampai dimusnahkan, diserahkan, atau dipreservasi secara sah; mendukung arsip fisik, digital-native, hasil digitalisasi, dan arsip hybrid. Setiap arsip harus autentik, andal, utuh, dapat digunakan, kontekstual, terlacak, aman, dan tertib retensinya. EDARMS bukan sekadar file-sharing/DMS.

**Prinsip wajib**:
1. Inspect before code; gunakan file, schema, alur, komponen yang sudah ada; no duplicate features; dokumentasikan gap.
2. Repository GitHub adalah source of truth. Setiap artefak yang berubah disimpan, commit SHA dilaporkan. Jangan berkata sudah ter-push bila belum ada SHA.
3. Production integrity first: tidak ada overwrite record yang sudah dideklarasikan; dokumen kerja boleh revisi dengan audit, record yang sudah final berubah melalui versi baru yang ditautkan.
4. No fabricated regulatory numbers: hukum dan JRA spesifik Bank ditandai VERIFY/TBD-BANK; persetujuan Legal, Compliance, Records Officer dan TI diperlukan.
5. Secure by design: default-deny, least privilege, data minimization, maker-checker, tenant isolation, evidence-preserving audit.
6. No fake functionality: semua tombol terlihat harus bekerja sesuai kontrak, dan memberikan validasi, feedback, loading, error, serta audit bila relevan.
7. No hard-coded live customer data, credentials, cloud secrets, production IDs, atau kunci. Data fiktif boleh hanya untuk PoC dan harus terisolasi.
8. Jangan memaksa public cloud untuk data rahasia Bank. Opsi deploy on-prem/private/hybrid mengikuti security review, kontrak dan kewajiban regulasi.
9. AI sebagai asisten: tidak boleh menghapus, menyetujui disposisi, mengesampingkan hold, atau mengubah JRA secara otomatis.
10. Buka akses implementasi untuk audit, export terbuka, backup-restore teruji, portability dan exit vendor.

**Mode**:
- PoC/Prototype: seed sintetis bertanda DEMO; sistem tetap punya backend/database nyata dan kontrol akses; larang koneksi ke data bank nyata dan larang klaim compliance.
- Enterprise Build: setelah baseline, JRA, role, data residency, metadata, volume, target RPO/RTO, serta owner kebijakan disetujui; jalankan migrasi dan release gate dengan bukti.
- Migration: bila kode lama ditemukan, hasil harus kompatibel atau direncanakan dengan migration & rollback, bukan mengganti seluruh repo secara serampangan.

# BAGIAN 1 — KETENTUAN & STANDAR SEBAGAI CONTROL MATRIX

Bangun Regulatory & Standards Register per item: instrument, nomor/tahun, otoritas, tanggal berlaku, pasal/ketentuan, kutipan ringkas terverifikasi, applicability bank, record series, technical control, rule version, control owner, evidence, test, status, reviewer, approval. Jangan mengklaim certified ISO dari sekadar mengikuti kontrol.

**Baseline awal untuk pemeriksaan legal**:
- UU 43/2009 Kearsipan; PP 28/2012; Peraturan ANRI 6/2021 Pengelolaan Arsip Elektronik (penyesuaian untuk BUMD).
- UU 8/1997 Dokumen Perusahaan; PP 87/1999 dan PP 88/1999. Ketentuan 10 tahun untuk kategori tertentu, bukan seluruh arsip.
- UU ITE beserta perubahan terakhir UU 1/2024; PP 71/2019 PSE.
- UU 27/2022 PDP, termasuk pengendalian dasar pemrosesan dan hak subjek dengan pengecualian hukum.
- POJK 11/POJK.03/2022 Penyelenggaraan TI oleh Bank Umum; PADK OJK 1/2026 (berlaku 1 Maret 2026, mencabut SEOJK 21/2017); SEOJK 29/SEOJK.03/2022 Ketahanan dan Keamanan Siber Bank Umum; POJK 8/2023 APU PPT PPPSPM sesuai scope.
- ISO 15489-1:2016; ISO 16175-1:2020; ISO/TS 16175-2:2020; ISO 23081-1:2017; ISO 14721:2025; ISO 27001:2022; ISO 22301:2019; prinsip ISO 27002 dan OWASP ASVS/WCAG 2.2 AA sebagai acuan desain.

**Rujukan resmi**: https://ojk.go.id/id/regulasi/Pages/PADK-1-Tahun-2026-Penyelenggaraan-Teknologi-Informasi-oleh-Bank-Umum.aspx ; https://ojk.go.id/id/regulasi/Pages/Ketahanan-dan-Keamanan-Siber-Bagi-Bank-Umum.aspx ; https://jdih.anri.go.id/peraturan/peraturan-arsip-nasional-republik-indonesia-no-6-tahun-2021 ; https://peraturan.bpk.go.id/Details/45929/uu-no-8-tahun-1997 ; https://www.iso.org/standard/74294.html .

Untuk setiap ketentuan, verifikasi *teks resmi yang berlaku*, peraturan pencabut/pengubah, scope BUMD/bank umum/BPR/BPRS, prosedur persetujuan dan bukti. Semua jadwal retensi, ketentuan alih media, klasifikasi keamanan, preservasi permanen, arsip vital, dan metadata wajib menunggu owner Bank. Aturan baru tidak boleh berpengaruh retroaktif secara diam-diam; wajib versioning dan impact assessment.

# BAGIAN 2 — ARSITEKTUR TEKNOLOGI & DELIVERY

**Stack default yang diusulkan, bukan klaim baseline**:
- Web: Next.js + React + TypeScript, TypeScript strict, server-side validation, i18n Bahasa Indonesia/English.
- UX: Tailwind CSS + komponen accessible setara shadcn/ui/Radix, icon Lucide, data-table virtualized/paginated, mobile-first.
- Backend: typed REST/OpenAPI (atau arsitektur modular setara yang diputuskan ADR), background workers & durable queues, idempotency keys, transactional outbox.
- Database: PostgreSQL transactional, migrations versioned, unique constraints, foreign keys, indexes, JSONB hanya untuk extensible metadata yang tervalidasi dan diindeks tepat.
- Object storage: S3-compatible private storage dengan encryption, object versioning/WORM-where-supported, retention lock, multipart, checksum, presigned links TTL pendek + otorisasi.
- Search: PostgreSQL full-text untuk fase awal atau OpenSearch/Meilisearch enterprise setelah benchmark; selalu ulang pemeriksaan ACL saat preview/download, bukan mengandalkan filter index.
- OCR: asynchronous worker / on-prem engine; simpan original dan turunan secara terpisah. AV scanning + MIME sniffing + anti-zip-bomb sebelum dipublikasikan.
- Auth: SSO OIDC/SAML IdP Bank; MFA, provisioning, session revocation, forced logout, break-glass logged.
- Encryption/key: TLS, encrypted at rest, KMS/HSM atau on-prem key custody, rotation, access logging, secret vault.
- Observability: trace ID, metrics, structured redacted logs, SIEM forwarding, audit sink independent.
- DevSecOps: GitHub PR review, CI, unit/integration/E2E, SAST/SCA/secret scan, migrations, stage/UAT/prod isolation, rollback plan.
- Deployment: container or managed environments yang ditetapkan Bank; tidak asumsikan Cloudflare Free/D1 atau layanan lain layak untuk data bank produksi.
- Storage and search isolation: pisahkan per bank; tenant ID di seluruh tabel/objek/indeks, scoped queries, negative tests. Pertimbangkan dedicated data plane bila diwajibkan kontrak.

**Repository layout sasaran** (adaptasikan ke existing):
apps/web; apps/api; apps/worker; packages/ui; packages/domain; packages/auth; packages/records; packages/retention; packages/audit; packages/config; db/migrations; docs/BRD; docs/SOP; docs/architecture; docs/regulatory; docs/UAT; docs/decisions; tests/unit; tests/integration; tests/e2e; .github/workflows.
Tidak membuat folder duplikat tanpa audit repo; struktur final dicatat ADR.

# BAGIAN 3 — PRODUK, NAVIGASI DAN DESIGN SYSTEM (WAJIB MENARIK, PROFESIONAL DAN USER-FRIENDLY)

**Identitas visual**: enterprise banking modern, elegant, trustworthy, tenang dan efisien; bukan landing-page poster atau terlalu banyak gradient. Default color tokens: Navy #10243A, Deep Navy #0B1726, Teal #008D9F, Accent Cyan #31B7CF, Warm Gold #B6955B, Off-white #F7F9FC, Surface #FFFFFF, Slate #64748B, Danger #B42318. Pastikan contrast ratio WCAG 2.2 AA; token dapat diatur admin/branding per Bank.

**Shell aplikasi**:
- Sidebar **kiri** fixed/collapsible (expanded 252–272 px, collapsed ~72 px); logo, menu per-role, active indicator, nested menu accordion, pin/favorites, hide/unhide, menu search; auto drawer pada layar kecil.
- Topbar sticky: breadcrumb, enterprise search global (Ctrl/Cmd+K), create-new shortcut, action inbox, notifications, help, bahasa, tema, profile user, logout yang benar-benar menghapus sesi.
- Main content: responsive 12-column grid, compact data-density switch, maximum line length terkontrol, header page jelas, helper text, action group dan filter.
- Desktop: dashboard cards, charts dan tables; tablet: responsive panels; Android/mobile: sidebar drawer, sticky bottom action khusus form, controls besar, keyboard tidak menutupi field.
- Typography: Inter / system font, body 14–16px, heading 20–28px; navigasi 14–15px; minimum touch target 44px; bentuk kartu radius 10–12px.
- Theme light/dark/system; high contrast; keyboard and screen reader support; focus visible; skip navigation; aria labels; color not sole indicator.
- Interaksi wajib: breadcrumb clickable, quick-filters, date picker locale Asia/Jakarta, combobox searchable, select multiple, sort/pagination/column settings, sticky table header, export indicator, confirm dialogs, upload dropzone, inline field errors, toast success/failure, skeleton load, empty/error/permission states, autosave draft (kalau aman) dan unsaved-changes warning.
- Tampilan data: date dd MMM yyyy, 24h WIB sesuai timezone user (simpan UTC), angka Indonesia, storage size, retention countdown, badge status dengan teks; sistem mendukung timezone kontekstual.
- Visual hierarchy: KPI bukan dekorasi; setiap kartu bisa drill-down ke filtered list yang benar. Grafik harus pakai angka dari database, bukan data statis.
- Login: login SSO atau akun internal jika kebijakan mengizinkan; MFA, forgot password tergantung IdP, lockout/rate limiting. Logout di menu profil dan navigasi mobile.
- Contoh home: KPI Arsip Aktif, Arsip Inaktif, Menunggu Klasifikasi, Akan Retensi, Legal Hold, Pengajuan Peminjaman, Pemusnahan Pending, Storage, OCR Queue, QA Exceptions; cards clickable ke list terkait.

**Reusable UI components**: AppShell, Sidebar, TopBar, Breadcrumbs, PageHeader, StatusBadge, KPICard, ChartCard, DataTable, FilterBar, ColumnChooser, DetailDrawer, FormSection, SmartSelect, DateRangePicker, FileDropzone, OCRReviewPane, RecordViewer, Timeline, ApprovalStepper, EvidencePanel, ConfirmationDialog, Toast, ErrorBoundary, AccessDenied, EmptyState, ActivityLogPanel, QRBarcodeLabel, SLAClock, HoldWarningBanner, DigitalSignatureStatus, SystemHealthCard.

**Universal page states**: loading, no-data with meaningful CTA, permission-denied, API timeout, concurrent-change/409, validation/422, session-expired/401, network offline, error retry. Never display blank page or faux success.

# BAGIAN 4 — INFORMATION ARCHITECTURE: SELURUH MENU / SUBMENU / FIELD / TOMBOL

Buat route untuk setiap submenu, navigation guard, breadcrumbs, detail page/drawer, server API, DB query, tests dan permissions. Semua menu tercantum minimal; kebijakan role mengatur visibility.

## A. Executive & My Workspace

**A1 Dashboard Eksekutif** — KPI arsip menurut status/seri/unit/cabang/kerahasiaan, tren ingest, kapasitas dan proyeksi, overdue SLA, legal hold, retensi, compliance maturity; filter Periode/Bank/Cabang/Unit/Jenis/Status; tombol [Terapkan Filter] [Reset] [Lihat Detail] [Export PDF] [Export XLSX] [Refresh]; setiap chart drill-down ACL-aware.
**A2 My Tasks & Approval Inbox** — tugas ditugaskan/didelegasikan/escalated, due date, approver, timeline; [Buka] [Setujui] [Tolak] [Kembalikan] [Delegasikan jika policy] [Pilih Banyak] [Export]; wajib alasan tolak dan larang self-approval.
**A3 My Records / Favorites / Recent** — akses hanya records authorized; [Buka] [Favoritkan] [Lepas Favorit] [Ajukan Akses] [Bagikan Internal] [Salin ID]. Recent access tidak menyimpan isi sensitif.
**A4 Notification Center** — filter unread/type/priority; [Tandai Dibaca] [Tandai Semua] [Buka Tugas] [Atur Preferensi] [Hapus Notifikasi dari UI] (tidak menghapus audit).

## B. Governance & Klasifikasi

**B1 Struktur Bank & Organisasi** — nama bank, kode, hierarki kantor/divisi/branch/unit, effective date, status; [Tambah] [Edit] [Nonaktifkan] [Pindah Unit] [Import] [Export] [Lihat Anak]; prevent orphan, cyclic parent, unauthorized reassignment.
**B2 Archival Policy & SOP** — jenis policy, nomor, versi, berlaku, pemilik, approval, dokumen lampiran; [Buat] [Upload] [Revisi] [Ajukan Review] [Setujui] [Publikasikan] [Tarik Publikasi] [Unduh] [Bandingkan Versi].
**B3 Kode Klasifikasi & File Plan** — level fungsi/aktivitas/transaksi/seri/file/item, kode unik, deskripsi, owner, confidentiality, template metadata; [Tambah Root] [Tambah Child] [Edit] [Pindah] [Mapping] [Nonaktifkan] [Import CSV/XLSX] [Export] [Preview Tree]; kode yang telah direferensikan tidak hard delete.
**B4 Record Series & Types** — kode seri, title, nilai guna, owner, keamanan, trigger event, default JRA, kewajiban permanen; [Tambah] [Edit] [Versi Baru] [Uji Rule] [Ajukan Persetujuan] [Aktifkan] [Arsipkan Konfigurasi].
**B5 Metadata Schemas** — data types, required/optional, validation regex, enums, dependencies, masking, full-text eligibility, field visibility; [Tambah Field] [Ubah Urutan] [Preview Form] [Validate Schema] [Ajukan] [Publikasikan Versi] [Rollback terkontrol] [Export Schema].
**B6 Access Classification & Regulatory Register** — security label, processing basis, matrix bank secrecy, risk owner; register peraturan dengan referensi pasal dan evidence; [Tambah Aturan] [Edit Draft] [Kirim Review] [Approve] [Lihat Dampak] [Export Control Matrix].

## C. Capture, Korespondensi & Digital Records

**C1 Kotak Masuk / Surat Masuk** — agenda nomor otomatis, tanggal terima, asal, tujuan, perihal, tingkat keamanan, lampiran, penyampaian/disposisi; [Registrasi] [Simpan Draft] [Kirim Disposisi] [Alihkan] [Tutup Agenda] [Cetak Agenda] [Buka Arsip].
**C2 Surat Keluar** — template naskah, nomor surat atomic, penandatangan, distribusi internal/eksternal, ekspedisi, tanda tangan; [Buat Surat] [Simpan Draft] [Ajukan Review] [Tanda Tangan] [Kirim] [Unduh PDF] [Batalkan dengan jejak].
**C3 Capture & Upload** — drag-drop, multi-file, batch scanner, inbound email/API, file source, case/series, metadata, checksum, duplicate detection, antivirus/quarantine, OCR queue; [Pilih File] [Upload] [Hapus dari Antrian] [Ulangi] [Simpan Draft] [Ajukan QA] [Batalkan] [Lihat Hasil Validasi]; file quarantine tidak masuk search.
**C4 QA & Record Declaration** — compare original/OCR, metadata check, signature verification, classification review, completeness; [Perbaiki Metadata] [Minta Revisi] [Tolak Ingest] [Terima] [Deklarasikan Arsip] [Lihat Checksum]; declared record immutable, audit & timestamps.
**C5 Digital Repository** — list/grid/tree, protected preview, 2-pane details, metadata, chronological revisions, related records, representasi file; [Buka] [Preview] [Unduh sesuai privilege] [Revisi Dokumen Kerja] [Buat Versi Terkait] [Request Reclassification] [Ajukan Akses] [Export Manifest] [Periksa Integritas].
**C6 Berkas / Case File** — kumpulan record per perkara/proyek/kredit/nasabah/kontrak, event-based closure, transfer ownership; [Buat Berkas] [Tambahkan Item] [Relasikan] [Tutup Berkas] [Buka Kembali dengan approval] [Ekspor Daftar] [Riwayat].
**C7 Bulk Ingest & Migrasi** — source system, mapping, preview, job metrics, error report, reconciliation; [Unggah Mapping] [Validasi] [Simulasi] [Jalankan] [Jeda] [Resume] [Retry Gagal] [Rollback batch yang eligible] [Export Exception]. Idempotency required.
**C8 Document Templates & Controlled Drafts** — template bank, surat, BA, cover, QR label, digital sign; [Buat] [Preview] [Revisi] [Setujui] [Aktifkan] [Duplikasi] [Pensiunkan].

## D. Physical Archives

**D1 Lokasi Penyimpanan** — site/gedung/lantai/ruang/row/rak/shelf/box, kapasitas, akses, climate/condition; [Tambah Lokasi] [Edit] [Nonaktifkan] [Generate Barcode] [Cetak Label] [Pindah] [Lihat Kapasitas].
**D2 Boks, Folder & Register Fisik** — nomor ID unik, series, dates, contents, security, condition, custodian; [Registrasi Boks] [Scan QR] [Tambah Berkas] [Pindah] [Segel] [Buka Segel Berizin] [Cetak Label] [Riwayat].
**D3 Peminjaman & Pengembalian** — requester, tujuan, tanggal, approver, penerima, due date, kondisi; [Ajukan] [Setujui] [Tolak] [Check-Out] [Perpanjang] [Check-In] [Laporkan Hilang/Rusak] [Cetak BA]; custody transfer perlu tanda terima.
**D4 Stock Opname & Condition Assessment** — scan mobile/QR, discrepancy, kondisi, lokasi aktual, evidence; [Buat Sesi] [Scan] [Catat Selisih] [Unggah Bukti] [Rekonsiliasi] [Setujui Selisih] [Tutup] [Export].
**D5 Transfer Fisik & Chain of Custody** — internal/antar kantor/pihak eksternal yang diizinkan, packaging, seal, tamper event; [Buat Transfer] [Cetak Manifest] [Serahkan] [Terima] [Tolak Terima] [Lihat Tracking] [BA Transfer].

## E. Pencarian, Permintaan & Layanan Pengguna

**E1 Global & Advanced Search** — kombinasi title/ID/metadata/OCR full-text/date range/series/unit/security/legal hold/type/status; typo tolerance di permitted scope, facets dan pagination; [Cari] [Reset] [Simpan Pencarian] [Lihat] [Preview] [Request Access] [Export Authorized]. Recheck ACL on every access.
**E2 Permintaan Dokumen** — purpose, requested record, authorized reviewer, deadline, delivery channel, watermark; [Ajukan] [Lampirkan Dasar] [Setujui] [Tolak] [Redaksi] [Berikan Akses Sementara] [Tutup] [Cetak Log].
**E3 E-Discovery & Collections** — legal matter/case, preservation scope, defensible collection, legal review, legal privilege; [Buat Case] [Scope] [Capture Collection] [Review] [Export Evidence] [Tutup] (hold release separately).
**E4 Akses Eksternal Terkendali** — auditor/regulator/law enforcement request dengan legal basis; [Registrasi] [Verifikasi] [Ajukan Legal Approval] [Redaksi] [Buat Paket] [Kirim Aman] [Cabut Link] [Audit]. No unaudited public links.

## F. Retensi, Legal Hold, Disposisi

**F1 Jadwal Retensi Arsip / JRA** — series, applicable sources, trigger event, active/inactive durations, permanent/transfer decision, exemptions, rule version, effective date, approvers; [Buat] [Edit Draft] [Simulasi] [Lihat Perubahan] [Ajukan] [Approve] [Publikasikan] [Pensiunkan].
**F2 Retention Calculator & Exception** — record ID, event source, effective rule, min expiry, max obligation, hold and blocking conditions; [Hitung Ulang] [Jelaskan Perhitungan] [Ajukan Koreksi Event] [Compare Rules] [Export]. Tidak hardcode tanggal upload sebagai trigger.
**F3 Legal Hold Register** — case, issuer, scope (record, series, customer, file, period, filters), reason, owner, review date; [Pasang Hold] [Edit Scope dengan approval] [Review] [Perpanjang] [Ajukan Release] [Approve Release] [Export Log]. Multiple holds supported. State hold orthogonal to record lifecycle.
**F4 Appraisal & Disposal Queue** — eligible candidates, rule, hold flags, evidence completeness; [Generate Kandidat] [Review] [Pilih] [Keluarkan] [Ajukan Disposal] [Kembalikan] [Setujui] [Tolak] [Generate BA]. Recheck before execution.
**F5 Pemusnahan & Evidence** — batch approved, authorized executor, dual witness where policy, physical/digital media, controlled erasure and backup policy; [Jadwalkan] [Verifikasi Ulang] [Eksekusi Berizin] [Catat Bukti] [Unggah BA] [Tandai Selesai] [Cetak Sertifikat]; irreversible action requires specific typed confirmation, dual approval, non-self-approval, live hold check + lock/transaction.
**F6 Transfer & Permanent Archive** — destination, manifest, authenticity, chain of custody, legal basis, AIP package; [Ajukan Transfer] [Setujui] [Generate Manifest] [Serahkan] [Konfirmasi Terima] [Tutup].
**F7 Exceptions & Permanent Records** — records stuck because dispute, overdue, missing metadata, rejected approval, retention conflict; [Lihat Alasan] [Ajukan Exception] [Upload Bukti] [Review] [Resolve] [Escalate].

## G. Preservasi & Integritas

**G1 Fixity & Integrity Monitor** — SHA-256 ledger, scheduled verification, corrupt/missing file, immutable objects, backups; [Jalankan Pemeriksaan] [Detail] [Karantina] [Mulai Recovery] [Verifikasi Recovery] [Download Evidence].
**G2 Preservation Plans & Format Migration** — file formats, obsolescence, derivative PDF/A where suitable, source hash preserved, migration evidence; [Buat Plan] [Uji Format] [Simulasi] [Minta Approval] [Jalankan] [Bandingkan] [Export Package].
**G3 Electronic Signature & Evidence Vault** — signer, signature type, validation timestamp/certificate chain, revocation checking, original proof; [Validasi] [Lihat Bukti] [Unduh Certificate] [Buat Evidence Package] [Kirim Terlindungi].
**G4 Backup & Restore Dashboard** — job history, snapshots, failed backups, retention, restore drills, RPO/RTO Bank; [Jalankan Uji Restore Terisolasi] [Lihat Status] [Download Report] [Buat Insiden]. Penghapusan/restore live produksi harus prosedur change-control.

## H. Audit, Compliance, PDP & Reporting

**H1 Audit Trail & Activity Ledger** — event immutability, actor, IP/device where lawful, UTC, correlation ID, object/record, old/new redacted metadata, reason; [Filter] [Cari] [Detail] [Export Authorized] [Verify Chain]. Tidak ada tombol delete audit event.
**H2 Compliance Control Matrix** — acuan, pasal, applicability, control, owner, test, due, evidence; [Tambah] [Edit Draft] [Mapping Control] [Attach Evidence] [Review] [Approve] [Export].
**H3 PDP & Confidentiality Desk** — register data categories, RoPA linkage, DPIA, data access request and lawful exception, incident privacy; [Register Activity] [Review Access] [Ajukan Data Subject Request] [Verify Identity] [Escalate Legal] [Complete with Evidence].
**H4 Operational & Regulatory Reports** — reports arsip aktif/inaktif/permanen, aging, SLA, retention due, destruction, custody, transfers, privacy, audit, compliance, storage; [Filter] [Preview] [Schedule] [Export PDF] [Export Excel] [Buat Signed Report]; report must respect ACL.
**H5 Risk, Incident & Follow-Up** — risks, controls, findings, action plans, owners, dates, evidence; [Tambah Risiko] [Laporkan Insiden] [Tetapkan Owner] [Update CAPA] [Review] [Tutup Temuan].
**H6 Service Level & Audit Evidence** — task metrics, response/resolution, approvals, audit exports, action reports; [Buat Evidence Pack] [Verifikasi Kelengkapan] [Download] [Lihat Historis].
**H7 Training & SOP Center** — portal prosedur & simulasi, policy acknowledgement, tests; [Cari SOP] [Baca] [Akui Sudah Membaca] [Ikuti Pelatihan] [Unduh Versi Terkendali].

## I. Intelligent Records & Search

**I1 OCR Queue & Quality** — file, engine, per-page results, language, recognition rate, thumbnail/bounding box, exception; [Jalankan OCR] [Ulangi] [Bandingkan] [Koreksi] [Simpan Koreksi] [Submit QA].
**I2 AI Classification Review** — suggested series/type, confidence, reasoning evidence spans, warnings; [Terima Usulan] [Ubah Manual] [Tolak] [Kirim ke Reviewer] [Lihat Model Version]. Human must finalize classification for high risk.
**I3 Semantic & Assisted Search** — approved source documents only, grounded citations to record+page, warnings, no cross-role leakage; [Tanya Arsip] [Buka Sumber] [Saring] [Laporkan Kesalahan] [Buat Saved Search].
**I4 Duplicate/Similarity Inspector** — cryptographic exact match, near-duplicates, similar text, source system; [Bandingkan] [Tandai Duplikat] [Buka Keduanya] [Batalkan Tanda] [Relasikan]. Jangan hard-delete basis similarity.
**I5 AI Models & Evaluation (Admin)** — providers, endpoint, model, residency, tasks, quota, encrypted keys, fallback, allowlist, prompt revisions, eval; [Tambah Provider] [Ubah] [Test Connection] [Enable] [Disable] [Set Priority] [Test Dataset] [Publish Prompt] [Rollback Prompt] [Audit]. Secrets never shown or included logs; no unapproved external provider enabled by default.

## J. Integrasi, Administrasi & Operasional Sistem

**J1 Integration Registry** — CBS/LOS/ECM/HRIS/ERP/email/e-sign/scanner/API, ownership, credentials via vault, data mapping; [Tambah Koneksi] [Test] [Enable] [Disable] [Update Mapping] [Lihat Log] [Retry Job] [Rotasi Kredensial].
**J2 API & Webhook Management** — scoped machine identities, client ID, callback endpoints, secrets stored securely, idempotency; [Create Client] [Set Scopes] [Rotate Secret] [Revoke] [Test Webhook] [Lihat Delivery] [Retry]. No plaintext token list.
**J3 User & Access Administration** — user identity, bank, unit, supervisor, role, group, expiry, status, MFA; [Tambah] [Undang] [Edit] [Nonaktifkan] [Reset MFA via controlled process] [Review Access] [Revoke Sessions] [Export List].
**J4 Role & Approval Matrix** — custom role, permission policy, separation of duties, delegation limits, step condition, thresholds from bank; [Buat Role] [Edit] [Simulasi Permission] [Ajukan Approval] [Aktifkan] [Compare Versions]. Developer/Admin cannot self-grant unreviewed destructive rights.
**J5 Master Data / System Parameters** — file type allowlist, size limits, SLA, classifications, localization, JRA references, branch, metadata, retention exceptions; [Tambah] [Edit] [Import] [Validate] [Approve Change] [Activate] [Rollback Version].
**J6 Workflow Builder** — maker-checker steps, escalation, delegation, parallel/serial, bounded loops, notification template; [Buat Workflow] [Tambah Step] [Simulasi] [Publish] [Deactivate] [Clone] [Lihat History].
**J7 Storage, Security & System Health** — job queue, space, failed integrations, indexing lag, retention lock status, metrics; [Refresh] [View Job] [Retry Eligible Job] [Pause Worker with Authorization] [Open Incident] [Download Diagnostics]; sensitive controls only privileged.
**J8 Branding, Localization & Preferences** — Bank logo, header, theme, default language, notification preferences, date/time and accessibility; [Upload Logo] [Preview] [Simpan] [Reset to Default] [Uji Kontras].
**J9 Notification Rules & Templates** — event triggers, channel email/in-app, recipients, urgency, quiet hours; [Tambah] [Edit] [Preview] [Test] [Aktifkan] [Nonaktifkan].
**J10 Help, Release Notes & Support** — changelog, documentation, support ticket, diagnostic ID; [Buka Panduan] [Buat Tiket] [Lampirkan Screenshot Aman] [Lihat Status].
**J11 Data Export, Portability & Exit** — complete archive export with original, derivatives, metadata JSON/CSV/XML where required, hashes, evidence, export manifest; [Buat Request] [Preview Scope] [Approve] [Mulai Export] [Verifikasi] [Download Package] [Hapus Paket Sementara sesuai kebijakan].
**J12 Tenant / Organization Provisioning** — only if multi-bank approved; tenant separation, classification, regional location, key custody; [Buat Tenant] [Review] [Aktifkan] [Suspend] [Transfer Ownership via controlled operation] [Uji Isolasi]. End-user cannot arbitrarily switch tenant.

**Total minimum menu**: 10 grup utama A–J dan 52 submenu (A4+B6+C8+D5+E4+F7+G4+H7+I5+J12). Peran tertentu hanya melihat menu yang berizin. Periksa dan hitung ulang daftar setelah implementasi.

# BAGIAN 5 — UNIVERSAL BUTTON & FORM CONTRACT (TIDAK ADA TOMBOL MATI)

**Setiap tombol/action** harus didaftarkan di Action Registry berkolom: route, action_id, label, role/scope, visibility condition, enabled condition, confirmation, mutation/API, validation, success UI, failure UI, audit event, test ID, sensitivity, owner. Semua onClick melakukan aksi nyata; jika service belum ada, jangan tampilkan enabled button atau berpura-pura sukses.

**Perilaku universal**:
- [Tambah/Buat]: buka form/modal yang memiliki schema, default aman, unique identifiers, Cancel dan Save; field wajib diberi label.
- [Simpan Draft]: persist ke DB, optimistic concurrency version/ETag, toast sukses + last saved; tidak mengubah status approved.
- [Simpan]: validasi di UI dan server; server menentukan auth dan status; tangani duplicate 409, validation 422, unauthorized 403.
- [Edit]: load current field+version; read-only fields jika declared/locked; track before/after dan reason.
- [Hapus]: soft-delete untuk konfigurasi/draft yang eligible saja; record declared tidak hard delete. Hapus permanen hanya via authorized disposal flow.
- [Ajukan/Submit]: validasi kelengkapan, create approval event, lock conflicting update, set status; prevent double-click with idempotency.
- [Setujui/Approve]: check active role, level, non-self-approval, version & condition, human decision; show what is approved.
- [Tolak/Reject]: alasan wajib, optional attachment, status and notification.
- [Kembalikan]: must select recipient/step and explain correction.
- [Batalkan]: withdraw eligible draft/request only; leave evidence if processing began; confirmation where necessary.
- [Unduh]: secure token/time-limited URL; recheck ACL, watermark for sensitive; log actor, file, time, reason; no direct public blob path.
- [Preview]: read-only safe renderer without browser executing embedded HTML/scripts/macros; mask/highlight allowed.
- [Upload]: MIME/extension/size/content checks, antivirus, checksum, quarantine, progress, retry/cancel, errors per-file.
- [Ekspor]: server-side authorized filters, async for large sets, sanitized CSV (formula injection safe), watermark and export audit.
- [Import]: sample template, preflight map, dry-run errors, duplicate strategy, transactional or recoverable execution.
- [Filter/Reset/Sort/Search]: update query and pagination correctly; persist view preferences without leaking data.
- [Bulk Actions]: explicit item selection with count, permission checks individually, partial failures summarized, do not bypass SoD.
- [Cetak/Label]: valid printable preview, barcode uniqueness, no hidden unauthorized metadata.
- [Share]: default internal authorized, expiry/access grant restrictions, never public open links by default.
- [Logout]: revoke server session/token as feasible, clear client state, redirect login; session idle/hard expiry.
- [Back/Close]: unsaved changes warning and safe return; modal focus trap and Escape.
- [Refresh]: invalidate active cache, show loading and request timestamp; no fake updates.
- [Retry]: safe idempotent retry, tracking job ID; do not duplicate approvals or destructive operations.
- Disabled button: show why disabled ("Anda tidak memiliki hak", "Arsip sedang legal hold", "Data belum lengkap"); hide rather than display prohibited privileged action when confidentiality requires.
- Destructive buttons require explicit impact summary, typed confirmation, approvals and transaction/revalidation at execution; no optimistic success or undo promise for irreversible action.

**Forms** must specify field_id, label, data type, required condition, min/max, source lookup, default, regex, data classification, visibility, help, validation message, dependency, masking, audit. Keyboard Enter, Tab and Esc work. Autosave drafts must not commit declarations or approvals.

**Table shared features**: pagination sizes 10/25/50/100 with server pagination, sortable columns, multi-filter, saved views scoped by user, column visibility, row selection, export authorized, bulk actions, total count, row action menu, empty state, sticky header, row link, responsive detail view. Never load entire confidential dataset into browser simply for filtering.

# BAGIAN 6 — ROLE BASED ACCESS & SEGREGATION OF DUTIES

Minimum roles configurable (multi-role with scope bank/unit/cabang/series/confidentiality/case):
1. System Super Admin (platform operations, no implicit right to see bank content);
2. Bank Admin (bank configuration, not unilateral destruction);
3. Records Manager / Unit Kearsipan;
4. Records Officer / Operator Arsip;
5. Unit Creator / Document Owner;
6. Reviewer / Checker;
7. Approver / Head of Unit;
8. Legal / Litigation Officer;
9. Compliance / Regulatory Officer;
10. DPO / PDP Officer;
11. Internal Auditor (read evidence, not destructive);
12. IT Security / SOC / DR Operator;
13. External Auditor / Regulator limited time/scope;
14. Employee / Requester;
15. Executive / Management;
16. Service Account integration (machine-only).

Buat permission matrix CRUD + execute + approve + export + share + decrypt + manage hold + disposal per role, scope, confidentiality and context. Tenant boundary selalu enforced. Authentication tidak sama dengan authorization. Policy engine supports explicit deny, inheritance and exceptions with time-bound approval. No privilege from frontend hidden fields. Every API, background job, search, preview, signed download, reporting and bulk action must re-evaluate privilege.

**SoD**: record creator ≠ final approver for the same controlled action; initiator disposal ≠ approver; legal hold issuer ≠ solo releaser if policy demands checker; system admin ≠ free content viewer; auditor ≠ editor; key custodian separated. Implement break-glass time-bound, justified, approved when feasible, alerted and reviewed.

# BAGIAN 7 — DATA MODEL, KEUNIKAN, CONSISTENCY & METADATA

Design ERD and SQL migrations with explicit FK, indexes, non-null constraints, tenant scope, classification scope, audit. At least:
- Identity: banks/tenants, organizational_units, users, role_bindings, policies, sessions, machine_clients.
- Governance: classification_nodes, record_series, metadata_schemas, metadata_fields, metadata_versions, policies, policy_approvals, regulation_sources, control_mappings.
- Records: case_files, records, record_versions, record_representations, file_objects, object_manifests, record_relationships, source_system_refs, intake_batches, ingest_exceptions, inbox/outbox/correspondence.
- Retention: retention_schedules, retention_rules, retention_versions, trigger_events, computed_retention, legal_holds, legal_hold_scopes, hold_events, appraisal_reviews, disposition_batches, disposition_items, disposal_certificates, transfer_manifests.
- Physical: buildings, rooms, shelves, bins, boxes, folders, physical_record_links, movements, checkouts, loans, custody_events, stocktake_runs, discrepancies, condition_reports.
- Workflow: workflows, workflow_versions, steps, approval_requests, decisions, delegations, task_assignments, notifications, SLA_definitions.
- Security & evidence: access_events, audit_events, audit_integrity_anchors, signatures, preservation_events, fixity_checks, security_incidents, privacy_requests, evidence_packages.
- AI/Jobs: ocr_jobs, ocr_pages, model_config, model_eval, classification_suggestions, review_decisions, search_index_jobs, integration_jobs, webhook_attempts, export_jobs.
- Config: settings_versions, reference_data, retention_policy_effective_dates, feature_flags, report_configs.

**Minimum metadata record**:
record_id, tenant_id, case_file_id, parent/series/classification, title, creator, owner_unit, event/created/received/captured dates, source_system/source_id, document_type, confidentiality, privacy categories, legal basis, declared_at/declared_by, active_state, physical location, retention trigger/date and rule version, disposal eligibility, hold indicators, related records, format, size, blob_sha256, representation_type, provenance, signed state, processing events.

Record hierarchy: Tenant/Bank -> Records Creator -> Function -> Activity/Series -> Case File -> Record -> Immutable Version -> Representation (original, OCR text, preview, preservation format) and side relation to physical item/location. Avoid placing all relations in one parent ID column without constraints.

**Transactional invariants**:
- Unique record numbers within tenant and configured series/period, generated by server atomic counter.
- Every declared record has at least one preserved immutable original, SHA-256, actor/time provenance and approved classification.
- Document deleted flag is NOT destruction; disposition record is distinct signed evidence.
- No orphan blob pointers, no missing event/approval foreign keys, no inaccessible evidence of deletion.
- Optimistic concurrency and transaction boundaries for changes, row/advisory locks for disposition.
- Multi-hold: hold active if ANY applicable scope active; one released hold never clears another.
- Retention policy changes are effective-dated and audited. Recompute with explicit impact review.
- Physical movement double-entry custody: from/to holder, timestamp, proof; physical location inventory is current projection, custody ledger is history.
- Search index lag cannot allow unauthorized access.
- Object keys unpredictable, not exposed as unprotected URL.
- Regulator/report snapshots include filters, creator, timestamp, rule version and checksum.

# BAGIAN 8 — DETERMINISTIC BUSINESS WORKFLOWS

**J1 Intake -> Capture -> Declare**: source -> virus scan -> checksum -> metadata & classification -> QA -> approved declaration -> lock original -> indexing -> evidence; invalid file quarantined; duplicate linked/flagged instead of blindly removed.
**J2 Correspondence**: draft surat -> review -> number reservation atomic -> sign -> dispatch -> capture as record -> closure.
**J3 Record Reclassification**: request -> calculate scope/access/JRA impact -> checker -> new classification with event trail, no deletion of old provenance.
**J4 Case Closure -> Retention Trigger**: close file with all prerequisites -> create trigger event -> evaluate approved series rule -> countdown -> review -> inactive.
**J5 Legal Hold**: authorized case -> scope/reason -> approval -> freeze disposition and applicable delete jobs -> regular review -> independent release -> recalc eligibility.
**J6 Disposal**: identify candidates -> verify policy/legal exceptions -> appraisal -> approval(s) -> freeze manifest -> just-in-time hold recheck -> execute method -> certify evidence -> reconcile replicas/derivatives/backups policy -> close; on partial failure mark PARTIAL/RECONCILIATION_REQUIRED and keep audit.
**J7 Physical Loan**: user request -> authorization -> scan checkout with custodian -> due/overdue reminder -> scan return -> assess condition -> close; missing/damaged -> incident.
**J8 Transfer & Accession**: select series/boxes -> manifest -> approval -> handover chain -> recipient acknowledgement -> update custody/location -> preserve evidence.
**J9 Digitization**: register original physical, scan/photo QA, validation, legal assessment of alih media, record representation linkage; no automatic permission to discard physical original.
**J10 E-Discovery/External Disclosure**: verify lawful request -> scope -> hold if needed -> reviewer -> redact authorized fields -> secure transfer -> access audit.
**J11 Subject Rights/PDP**: receive -> verify identity -> identify records -> evaluate lawful obligations/exemptions/holds -> approve response -> evidence; erasure cannot bypass statutory recordkeeping.
**J12 AI Human-in-the-loop**: OCR -> proposed metadata & code -> confidence policy -> human review -> approve classification -> store model version/evidence. Retention/destruction never decided by model.
**J13 Backup, Restore, Disaster**: scheduled backup -> integrity verification -> isolated restoration rehearsal -> compare DB/blobs/audit -> sign report -> escalation; change approval for live recovery.
**J14 Integration Retry**: webhook receives signed request -> deduplicate -> validate -> process -> outbox event -> retry exponential with dead-letter and manual review; no duplicated records.
**J15 API Export & Exit**: export request -> auth -> snapshot scope -> package original+metadata+hash+chain custody -> verify manifest -> secure delivery -> expiry.

**Retention decision pseudorules in natural language**:
1. Resolve effective approved JRA by record series, category, branch and event date.
2. Gather legal/contractual/regulatory minima and active exceptions; use the most restrictive applicable retention obligation where duration can be compared; conflict -> legal review queue.
3. If trigger event unknown, status RETENTION_TRIGGER_MISSING, never assume capture date.
4. Compute eligibility from actual trigger and approved durations, preserve rule trace.
5. If permanent, transfer needed, investigation, open audit, pending legal/regulator instruction, OR any active hold -> BLOCKED.
6. Disposal only with two independently authorized approvals, just-in-time reevaluation, signed destruction evidence.
7. If policy updated, recomputation preview and impact sign-off before changes apply.

# BAGIAN 9 — KEBUTUHAN KEAMANAN, PRIVASI DAN RESILIENSI

- Threat model STRIDE/abuse cases: IDOR/BOLA, role spoofing, tenant switching, malware embedded document, XSS via metadata/OCR, CSRF, SSRF via connector URL, SQL injection, path traversal, signed URL leakage, CSV formula injection, storage race conditions, background-job bypass, approval forgery, hash substitution, untrusted prompt injection.
- Defenses: safe rendering, sanitization/escaping, CSP, server validation, anti-CSRF on cookie sessions, rate limiting, secure headers, user session control, MFA, KMS, audit, short-lived object access, consent/privacy exception.
- Scan upload for malicious payloads; no executable preview; disallow archives/macros unless explicitly allowed and isolated; process OCR workers sandboxed.
- Confidentiality labels: Publik, Internal, Terbatas, Rahasia, Sangat Rahasia (parametrisasi Bank); field redaction, access justification, time-limited grants, watermark print/export.
- Privacy: purpose limitation, DSR/ROPA/DPIA support, mask personal identifiers, no customer data in logs, AI providers, client analytics or dev tools without lawful basis/approval.
- Audit integrity: append-only sink, privileged access segregation, tamper-evident chaining and periodic verification; tested export for regulators.
- Encryption: keys separated by environment and tenant if required; rotation and backup; never log plain secrets; never commit .env.
- Backup DR: DB + blob + object-lock configs + indexes rebuild + audit event recovery; immutable/offline backups, documented RPO/RTO TBD-BANK; actual isolated restore drills.
- Security testing: SAST, DAST/VA-PT as appropriate, SCA, dependency pinning, secret scan, RBAC negative tests, tenant isolation, misuse tests, DR game day.
- Vendor governance and data residency: document DPA/contract, rights to audit, incident response, vendor exit and subcontractors; external AI off by default.
- Availability/performance/capacity targets all TBD-BANK after volumes assessed. No hardcoded fake 99.9% claims.

# BAGIAN 10 — API, JOBS, EVENT CONTRACTS

Specify OpenAPI 3.1 with resources: /auth, /users, /roles, /org-units, /classifications, /series, /schemas, /policies, /records, /records/{id}/versions, /cases, /ingest/batches, /physical/locations, /physical/boxes, /physical/movements, /loans, /search, /requests, /retention/rules, /retention/evaluations, /holds, /dispositions, /transfers, /preservation, /fixity, /audit, /privacy, /reports, /ai/ocr, /ai/reviews, /integrations, /jobs, /admin/settings.

API standards:
- IDs ULID/UUID, cursor or keyset pagination, field validation, canonical error {code, message, trace_id, field_errors}, pagination metadata, filter whitelists and deterministic sorting.
- Every mutating API: authenticated, authorized, idempotency key for create/critical operations, optimistic version checking and audit event.
- API results must omit redacted fields and forbidden records; 404 vs 403 behavior prevents information disclosure.
- Presigned URLs generated only after authorization, expire quickly, cannot be reused for public distribution by default.
- Batch jobs: QUEUED, VALIDATING, RUNNING, PAUSED, PARTIAL, COMPLETED, FAILED, CANCELLED with timestamp and item-level exceptions; safe retry.
- Webhooks: signatures, allowlist, replay protection, delivery attempts, DLQ, minimum payload PII.
- Structured events: record.captured, record.declared, record.reclassified, case.closed, retention.calculated, hold.applied, hold.released, disposition.approved, disposition.executed, loan.checked_out, loan.checked_in, file.fixity_failed, access.denied, data.exported, privacy.requested, security.incident.
- Transactional outbox ensures state change and event issuance consistent. Version every event schema and API.

# BAGIAN 11 — RANCANGAN UI DETAIL, HALAMAN, BUTTON TEST

For every A1–J12 submenu implement and document:
1. Route, title, short task description, role scope, breadcrumbs and contextual help.
2. Responsive layout annotated wireframe or screenshot; list/detail/create/edit and empty/loading/error versions.
3. All fields with types, required flags, defaults, enums, dependencies, autocomplete sources, limit, privacy level, field-level mask and server rules.
4. All top buttons, row action buttons, bulk actions, filter controls and context menus; produce Action Registry with action_id, intended result, API, validation, permission, feedback, error, audit.
5. Lists: search, sorting, filter, pagination, count, export, saved views, selection, zero results CTA and role-aware column settings.
6. Forms: Save Draft, Save, Submit, Cancel, Back, Undo draft where safe, change-warning; show unique ID / error.
7. Review controls: approve, reject with reason, return for correction, delegate only if allowed, status history, signature validation.
8. Document viewer: metadata drawer, page navigation, zoom, thumbnails, rotate view, text select/search, redaction overlay, watermark, download request, no unauthorized print.
9. Physical UI: scan barcode via supported camera, manual fallback, QR result disambiguation, offline clearly labeled and safe sync with conflict resolution.
10. Buttons must have automated click/E2E tests. Use real DB fixture, reject unauthorized action, verify state and audit event.
11. UI acceptance: no overflow in 360px viewport, no clipped fields on Android keyboard, menu hide/unhide, accessible focus, light/dark, loading states, toast, error retry, logout, all links valid.
12. Navigation check: no sidebar empty route, no 404 menu, no dormant controls. Feature-flag unfinished screens and label as not released; do not display "success" without commit.

**Mandatory Action Test Matrix** example:
- Upload original -> AV/checksum/metadata validation -> job queued -> file status -> test malware DENY, duplicate and empty file.
- Save Draft -> valid row in DB -> toast/dirty flag reset -> refresh persists.
- Declare Record -> QA approved -> immutable checksum -> wrong role DENY -> audit event.
- Reclassify -> impact preview and approval -> metadata and derived retention recalculated with evidence.
- Approve Disposal -> maker≠checker -> hold check -> no self approval -> 409 on stale record.
- Execute Destruction -> two approvals + valid batch + no hold + lock -> certificate -> partial failure retained.
- Loan Check-Out -> scan and custodian ack -> new location -> unauthorized checkout DENY.
- Export -> only authorized records -> packaged metadata/hash -> trace/audit evidence.
- AI Accept Suggestion -> human actor saved, confidence and model provenance attached, never destructive.
- Logout -> session revoked and restricted pages inaccessible after back navigation.

# BAGIAN 12 — QA/UAT, QUALITY GATES, EVIDENCE

**Testing layers**: unit domain rules, integration DB/queues/object store, contract API, end-to-end Playwright, accessibility axe, cross-browser Chromium/WebKit, Android responsive, load & stress with synthetic data, restoration integrity, tenant isolation, threats and failure injection.

**UAT minimum suites (target initial, adjust with Bank)**:
- UAT-001–040 governance, classification, metadata, policy versioning;
- UAT-041–100 incoming/outgoing, capture, QA, digital records and search;
- UAT-101–145 physical locations, box, custody, loans, stock opname;
- UAT-146–205 retention, multiple holds, permanent records, disposal, transfer;
- UAT-206–245 preservation, signature evidence, fixity, restore;
- UAT-246–290 access, privacy, security, reports, admin;
- UAT-291–330 AI/OCR, integration, batch export and mobile usability.
Total design baseline: **330 scenarios**, each with test ID, precondition, role, synthetic fixture, steps, expected UI/API/DB/audit, evidence path, result, defect, retest. 330 adalah target desain skenario, bukan klaim test sudah dibuat/lulus.

**P0 adversarial scenarios**:
1. Maker self-approve disposal fails;
2. second active hold blocks after first released;
3. hold arrives mid-disposal job, execution recheck aborts;
4. forged record ID from other tenant yields deny even signed download;
5. unauthorized search facets/record count not leaked;
6. privileged system admin cannot alter sealed evidence;
7. MIME spoof/zip bomb quarantined;
8. stale edit yields conflict not silent lost update;
9. expired external share denies;
10. OCR prompt injection cannot instruct AI to bypass policies;
11. permanent record not eligible disposal;
12. retention trigger absent -> cannot dispose;
13. restore mismatch triggers incident;
14. record hash corruption alerts;
15. bulk operation partial failure reconciles without lost audit;
16. PDF/Office preview cannot execute script;
17. CSV export sanitized;
18. log export cannot disclose secret;
19. duplicate webhook does not duplicate records;
20. mobile save/keyboard/sidebar tests pass.

**Quality gates**:
- Build/typecheck/lint/tests CI pass and migration verified.
- No unresolved critical/high security findings without documented bank-approved exception (prefer zero).
- 100% mandatory P0 scenarios pass in UAT; each UI action and role negative case has tests.
- No critical retention/hold/destruction/integrity issue open.
- Restore drill passing with Bank-defined RPO/RTO evidence.
- Volume/performance, observability, metadata integrity and audit export meet Bank-approved objectives.
- Legal/Records Officer/Compliance/IT Security sign-off before production.
- Rollback and recovery plans documented and rehearsed; no production deploy merely because GitHub push succeeded.

# BAGIAN 13 — WORK PACKAGES / SPRINT EXECUTION

**WP0 — Discovery & Baseline (P0)**: audit repo, inspect code if exists, verify dependencies, regulatory matrix, BRD, RACI, personas, data series/JRA sample, environment, threat model, target architecture ADR, UX sitemap, Action Registry, UAT skeleton. Deliver: BRD, FR/NFR, ERD, navigation spec, control matrix, decisions. Gate: reviewer sign-off for assumptions / TBD-BANK.
**WP1 — Platform Foundation (P0)**: scaffold or improve stack, identity, RBAC/ABAC, session/logout, tenant isolation, seed synthetic, audit events, API error conventions, CI, base design system and sidebar, dashboard placeholders only when honestly labeled.
**WP2 — Archive Governance (P0)**: master org, taxonomy, series, metadata schema, policies/JRA versioning, rights, admin settings.
**WP3 — Digital Capture & Records (P0)**: correspondence, batch ingestion, malware scanner, checksum, metadata, QA, immutable declaration, version management, case files.
**WP4 — Retention & Legal (P0)**: event triggers, JRA engine, hold and exceptions, appraisal and maker-checker disposition with evidence, negative tests.
**WP5 — Physical & Requests (P1)**: physical hierarchy, barcode, custody, stocktake, loans and transfers, controlled access request/search.
**WP6 — Preservation, Evidence & Compliance (P1)**: fixity, file format strategies, evidence packages, audit ledger verification, PDP workflow, regulatory control mapping, reports.
**WP7 — AI/OCR & Integration (P2/P1)**: controlled OCR, human AI review, semantic search scoped, integrations, bulk migration/exit, evaluation.
**WP8 — Security/Resilience/UAT (P0)**: comprehensive tests, accessibility, VA/PT, performance, DR restore, change control, role UAT, documentation/training.
**WP9 — Controlled Release (conditional)**: staged pilot with synthetic or authorized data, migration reconciliation, sign-offs, rollback, then bank-approved production release and operational handover.

Work each WP vertically: DB -> API -> UI -> actions -> role controls -> error states -> tests -> docs -> commit. If regulatory or bank-specific inputs missing, isolate configuration as VERIFY/TBD-BANK and continue safe PoC parts; do not fabricate legal permissions. No fake placeholders presented as done.

# BAGIAN 14 — DEFINITION OF DONE PER FITUR

A feature is DONE only if: route accessible to authorized role; controls render; fields validate; API mutation persists; appropriate permissions fail closed; relationships consistent; event audit exists; success/error/empty/loading states; responsive keyboard; unit+integration+E2E tests; document help; UAT evidence; docs updated; commit SHA on repo. Approval of retention/legal logic requires owner sign-off, not merely passing code tests.

**End-of-WP report format**:
1. WP and features with status DONE/PARTIAL/BLOCKED;
2. repository branch & commit SHA(s) and changed files;
3. verified UI routes and actions with test IDs;
4. migrations & tests run plus PASS/FAIL/NOT RUN honest;
5. security findings and remediation;
6. remaining VERIFY/TBD-BANK decisions and owners;
7. demo URLs only if deployed and accessible, actual verification;
8. next WP and release gate.

# BAGIAN 15 — PARAMETER BANK WAJIB SEBELUM OPERASIONAL NYATA

TBD-BANK-001 legal organization type and office hierarchy; TBD-BANK-002 archival classification/file plan; TBD-BANK-003 approved record series and JRA including trigger; TBD-BANK-004 permanent records and transfer procedures; TBD-BANK-005 physical destruction/legalization; TBD-BANK-006 confidentiality and privileges; TBD-BANK-007 identity provider/MFA; TBD-BANK-008 SSO/roles/SoD; TBD-BANK-009 object storage & key custody; TBD-BANK-010 bank-approved hosting/data location; TBD-BANK-011 RPO/RTO & backup; TBD-BANK-012 archival volumes, data formats & load; TBD-BANK-013 source integration owners; TBD-BANK-014 approved OCR/AI/residency; TBD-BANK-015 security/privacy policy & incident response; TBD-BANK-016 acceptance criteria signatories; TBD-BANK-017 organizational metadata required fields; TBD-BANK-018 signature/BA retention & evidentiary format; TBD-BANK-019 branch coverage, multi-tenancy policy; TBD-BANK-020 production release approval.

# BAGIAN 16 — PERINTAH PELAKSANAAN CODING AGENT

**Segera lakukan**:
1. Read actual HEAD and repository instructions from GitHub DRM; inspect current tree and document status. Do not assume this prompt equals working implementation.
2. Create/update docs/BRD/EDARMS-BRD.md, docs/regulatory/control-matrix.md, docs/architecture/ERD.md, docs/UX/navigation-and-action-registry.md, docs/UAT/master-scenarios.md, docs/decision-log.md, CHANGELOG.md where relevant.
3. Produce full inventory for all 52 screens/menus and EVERY button including conditional permissions and API contract. Recount IA actual.
4. Implement WP0 then WP1 and onward incrementally; maintain tight commits and guardrails; if approval absent, build only safe PoC features with synthetic fixtures.
5. No premature production deployment; release contingent on gates and Bank approval.
6. Ensure all available tests are actually executed; state NOT RUN when runner unavailable.
7. At every stop output the end-of-WP report; commit actual changes to GitHub with SHA and links.
8. Do not end at generic advice, nonfunctional screens or dead buttons. Build real, secure, auditable workflows and follow the next WP where dependencies permit.

**Final outcome**: EDARMS enterprise-grade, safe, accessible, scalable, auditable, able to manage physical and digital records end-to-end, with deterministic and bank-approved retention and legal hold, evidence-backed disposition, and user-friendly interfaces for all roles.
