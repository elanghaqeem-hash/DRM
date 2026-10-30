# AUDIT & REKOMENDASI ENTERPRISE DRM — 30 Oktober 2026

**Repository:** https://github.com/elanghaqeem-hash/DRM  
**Branch baseline:** `main`  
**Ruang lingkup:** audit awal repository, gap tata kelola arsip fisik dan digital, arsitektur sasaran, kepatuhan regulasi/standar, backlog, kriteria penerimaan, dan roadmap.  
**Status laporan:** assessment awal / preliminary technical and functional gap assessment. **Bukan** opini legal final, hasil penetration test, atau sertifikasi kepatuhan bank.  
**Referensi waktu:** ketentuan yang diverifikasi melalui sumber resmi per 30 Oktober 2026. Semua nilai spesifik bank tetap `TBD-BANK`.

## 1. Ringkasan temuan aktual (fakta hasil pemeriksaan)
- Repository publik `elanghaqeem-hash/DRM` terhubung, default branch `main`, akses baca/tulis tersedia.
- `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/decision-log.md` tersedia. ADR-0001 menetapkan repository sebagai sumber kebenaran proyek; ADR-0002 masih Proposed.
- `README.md` dan `CHANGELOG.md` mengonfirmasi baseline aplikasi, stack, skema DB, test suite, CI/CD, dan deployment masih pending.
- `package.json`, `wrangler.toml`, `drizzle.config.ts`, `.github/workflows/ci.yml`, `docs/architecture.md`, `docs/BRD.md`, dan `docs/regulatory-matrix.md` tidak ditemukan pada `main` melalui pemeriksaan path.
- Karena belum ada aplikasi yang dapat diuji, **status setiap fitur, keamanan, UAT, availability, backup/restore dan produksi adalah NOT VERIFIED**, bukan otomatis FAIL. Tidak ada pengujian runtime yang dilakukan pada assessment ini.

**Keputusan audit:** repository belum menunjukkan bukti sistem DRM operasional. Mulai dengan kebutuhan dan control model yang dapat diuji sebelum pembangunan modul atau deployment produksi.

## 2. Target product dan batas penting
Nama sasaran: **Enterprise Digital Archives & Records Management System (EDARMS)**.

Sistem bukan sekadar DMS/file sharing. Ia harus menjaga **keautentikan, reliabilitas, integritas, kegunaan, konteks, kepemilikan, ketertelusuran, masa simpan, serta disposisi** setiap arsip sepanjang siklus hidup. Bedakan dokumen kerja yang masih berubah dengan record yang telah dideklarasikan (record capture/lock).

Lingkup arsip **fisik**, **digital-native**, **alih media/hasil pindai**, dan **hybrid**, termasuk korespondensi, kontrak, administrasi keuangan, dokumen kredit, dokumen nasabah, operasional cabang, HR, GRC, audit, legal, vendor, CCTV/evidence, dan dokumen regulator sesuai kebijakan Bank.

## 3. Gap dan kontrol yang perlu diimplementasi

| ID | Domain | Kondisi terverifikasi | Target kontrol | Prioritas |
|---|---|---|---|---|
| A01 | Governance dan policy | Belum ada BRD definitif | RACI pencipta arsip/unit pengolah/unit kearsipan/approver/legal/DPO/audit dan katalog SOP | P0 |
| A02 | Classification dan file plan | Belum ada implementasi | Hierarki fonds/creator > fungsi > seri > berkas > item; kode klasifikasi; crosswalk unit & sistem sumber | P0 |
| A03 | Metadata | Belum ada implementasi | Skema metadata wajib, enumerasi, validasi, provenance, versi skema | P0 |
| A04 | Ingestion | Belum ada implementasi | Batch upload/API/email/scanner, fingerprint, checksum, AV, quarantine, OCR turunan, quality review | P0 |
| A05 | Declaration & version | Belum ada implementasi | Draft -> review -> declared immutable; revisi sebagai versi baru, tidak overwrite bukti | P0 |
| A06 | Auditability | Belum ada implementasi | Event append-only, actor, timestamp UTC, before/after, alasan, integritas bukti | P0 |
| A07 | Access & bank secrecy | Belum ada implementasi | SSO/MFA, least privilege, RBAC+ABAC, row/field/document security, SoD, dual control | P0 |
| A08 | Retention & JRA | Belum ada implementasi | Retensi berbasis seri, event trigger, dasar hukum, prioritas rule, effective date, review | P0 |
| A09 | Legal hold | Belum ada implementasi | Hold multi-scope, otorisasi legal, freeze pemusnahan termasuk background jobs, release tercatat | P0 |
| A10 | Disposition | Belum ada implementasi | Eligibility evaluation -> review -> approval -> 4-eyes -> destruction/transfer -> berita acara & certificate | P0 |
| A11 | Physical records | Belum ada implementasi | Gedung/ruang/rak/boks/folder, barcode/QR, peminjaman, checkout, chain of custody, stock opname | P1 |
| A12 | Discovery | Belum ada implementasi | Full text + metadata, ACL-aware search, ekspor terkendali, masking | P1 |
| A13 | Preservation | Belum ada implementasi | Format preservation, PDF/A where appropriate, fixity check, checksum-repair, format migration, signature evidence | P1 |
| A14 | Regulatory & privacy | Belum ada implementasi | Control register, RoPA, DPIA, data subject request workflow with legal exceptions, traceability | P0 |
| A15 | Integration | Belum ada implementasi | API idempotent, CBS/LOS/DMS/HRIS/ERP/ECM/email/e-sign, connectors dengan ownership jelas | P1 |
| A16 | Security operations | Belum ada implementasi | KMS, encryption at rest/in transit, SIEM, DLP, anti-malware, DR & restore rehearsal, break-glass | P0 |
| A17 | AI assistance | Belum ada implementasi | OCR/classification suggestion with confidence, human validation, no automated destruction | P2 |
| A18 | Delivery governance | Belum ada code/test | CI/CD, migration, seeded fictional PoC, tests, SAST/SCA, access negative tests, UAT evidence | P0 |

Klasifikasi P0/P1/P2 merupakan **prioritas rekomendasi**, bukan hasil audit uji fitur.

## 4. Daftar modul/menu sasaran
1. Dashboard & Compliance Cockpit.
2. Organizational Structure & Archival Governance.
3. Master Data & Configuration (unit, taxonomy, file plan, seri, klasifikasi, metadata, JRA, dasar hukum, lokasi fisik, tipe berkas, keamanan).
4. Record Capture / Incoming & Outgoing / Correspondence.
5. Digital Records Repository & Version Management.
6. Physical Archives & Warehouse / Box / Barcode / Loan.
7. Classification & Metadata Quality.
8. Search, Retrieval, Controlled Preview & Export.
9. Retention Schedule / JRA Engine.
10. Legal Hold, E-Discovery & Investigation.
11. Appraisal, Transfer, Disposal & Destruction.
12. Preservation, Integrity & Format Migration.
13. Approval Workflow, E-Signature & Evidentiary Package.
14. Records Requests / Borrowing / Access.
15. Source System Integration & Bulk Migration.
16. Privacy, Bank Secrecy & Sensitive Records.
17. AI/OCR & Human Review Queue (opt-in).
18. Audit Trail, Risk, Compliance & Regulatory Reporting.
19. Administration, Identity, Roles, API Keys, Monitoring, Backup/DR.
20. SOP/Policy Center & Training / Audit Evidence.

## 5. Model data inti dan aturan bisnis

### Entitas inti
`Tenant/Bank`, `OrgUnit`, `User`, `Role`, `AccessPolicy`, `RecordsCreator`, `ClassificationCode`, `RecordSeries`, `CaseFile`, `Record`, `RecordVersion`, `RecordRepresentation`, `ObjectBlob`, `MetadataSchema`, `MetadataValue`, `RetentionSchedule`, `RetentionRule`, `RetentionEvent`, `LegalHold`, `HoldScope`, `DispositionBatch`, `DispositionDecision`, `ApprovalStep`, `PhysicalLocation`, `Box`, `Movement`, `Loan`, `ChainOfCustodyEvent`, `PreservationEvent`, `AccessEvent`, `AuditEvent`, `EvidencePackage`, `IntegrationJob`, `RegulatoryControl`, `ControlEvidence`.

### Metadata minimum
`record_id` (stabil), `tenant_id`, `creator_id`, `owning_unit`, `classification_code`, `series_id`, `case_file_id`, `title`, `description`, `document_type`, `event_date`, `capture_time`, `source_system`, `record_status`, `confidentiality_level`, `PII_class`, `legal_basis`, `retention_rule_id`, `retention_trigger`, `hold_status`, `blob_sha256`, `storage_key`, `signature_validation_status`, `provenance`, `physical_location_id`, `created_by`, `last_accessed`, `disposition_status`.

Dukung metadata multi-valued untuk pihak terkait, kontrak, fasilitas kredit, agunan, kasus, tanggal efektif, dan relasi silang. Identitas nasabah/NIK perlu proteksi field-level dan pencarian terbatas, tidak di-log mentah. Untuk dokumen yang belum dideklarasikan, izinkan pembaruan dengan audit; untuk record yang telah dideklarasikan, perubahan konten harus jadi versi baru/derivative yang ditautkan.

### Model lifecycle
`DRAFT -> CAPTURED -> QA_REVIEW -> DECLARED_ACTIVE -> INACTIVE -> RETENTION_REVIEW -> {TRANSFERRED | DISPOSAL_APPROVED | PERMANENT_PRESERVATION}`; `LEGAL_HOLD` adalah status penahanan orthogonal, bukan state yang menggantikan lifecycle. Destruction hanya oleh job berotorisasi setelah eligibility check paling akhir. Pemusnahan tidak boleh dipicu oleh OCR/AI.

### Aturan retensi
1. Semua seri punya jadwal retensi yang telah disetujui dan versi berlakunya.
2. Hitung `start_date` dari event yang valid (penutupan berkas, akhir tahun buku, akhir kontrak, terminasi hubungan, penyelesaian perkara, atau trigger spesifik) bukan selalu tanggal unggah.
3. Hitung seluruh kewajiban minimum yang relevan, ambil jangka wajib terpanjang. Kaji litigasi/tuntutan yang sedang berlangsung serta pengecualian hukum.
4. Jika ada **legal hold, investigasi, audit tertunda, perintah regulator, arsip permanen, perubahan retensi yang belum disahkan, atau sengketa**, blokir pemusnahan.
5. Penghapusan data pribadi tunduk pada dasar hukum, tujuan, kewajiban retensi, hak subjek data, serta pengecualian yang sah; jangan implementasikan `right-to-erasure` sebagai bypass retensi wajib.
6. Approval tidak boleh oleh pencipta arsip yang sama (maker-checker). Semua keputusan ditandatangani/tercatat.
7. Hapus semua kopi yang wajib dihapus (termasuk turunan/search/backup sesuai desain) dengan mekanisme yang menjaga kewajiban backup & retensi; catat *deletion manifest*. Tidak mengklaim penghapusan menyeluruh sebelum mekanismenya diverifikasi.

## 6. Regulasi dan standar — baseline rujukan (bukan sertifikasi)
| Acuan | Subjek | Konsekuensi desain | Sifat |
|---|---|---|---|
| UU 43/2009 + PP 28/2012 | Kearsipan | siklus hidup, klasifikasi, JRA, penyusutan, daftar arsip, tata kelola | wajib sesuai lingkup organisasi |
| Peraturan ANRI 6/2021 | Pengelolaan arsip elektronik dalam lingkup regulasi | arsip elektronik, metadata, tata kelola; relevansi khusus BUMD perlu dijabarkan | wajib jika masuk subjek regulasi |
| UU 8/1997 Pasal 11 | Dokumen perusahaan | catatan, bukti pembukuan dan data pendukung keuangan tertentu 10 tahun sejak akhir tahun buku; dokumen lainnya menurut jadwal retensi / nilai guna | wajib sesuai jenis dokumen |
| PP 87/1999 | Penyerahan & pemusnahan dokumen perusahaan | approval, berita acara, bukti pelaksanaan | wajib sesuai lingkup |
| PP 88/1999 | Alih media & legalisasi dokumen perusahaan | autentikasi dan prosedur alih media; scan tidak otomatis menggantikan asli | wajib sesuai lingkup |
| UU ITE 11/2008 beserta perubahan, terakhir UU 1/2024; PP 71/2019 | Informasi/transaksi elektronik dan penyelenggaraan sistem | integritas, bukti elektronik, audit, TTE bila diperlukan | wajib sesuai lingkup |
| UU 27/2022 | Pelindungan data pribadi | data minimization, dasar pemrosesan, RoPA, DPIA berbasis risiko, akses/hak subjek dan safeguards | wajib sesuai lingkup |
| POJK 11/POJK.03/2022 | Penyelenggaraan TI bank umum | tata kelola TI, keamanan, risiko vendor, penempatan data, kontrol & audit | wajib bank umum |
| PADK OJK 1/2026 (berlaku 1 Maret 2026) | Pedoman TI bank umum | detail tata kelola, arsitektur, vendor, keamanan, pelindungan data, kontrol & pelaporan; **mencabut SEOJK 21/2017** | wajib bank umum |
| SEOJK 29/SEOJK.03/2022 | Ketahanan dan keamanan siber bank umum | pengujian siber, respons insiden, ketahanan | wajib bank umum |
| POJK 8/2023 | APU PPT PPPSPM | dokumentasi dan akses rekam jejak untuk kebutuhan kepatuhan | wajib sesuai produk/subjek |
| ISO 15489-1:2016 | Records management principles | proses & policy | acuan best practice |
| ISO 16175-1:2020 | Persyaratan fungsi aplikasi records | functional requirements design/UAT | acuan best practice |
| ISO/TS 16175-2:2020 | Seleksi, rancangan, implementasi, pemeliharaan software records | implementation approach | acuan best practice |
| ISO 23081-1:2017 | Metadata untuk records | metadata governance | acuan best practice |
| ISO 14721:2025 | OAIS preservation model | preservasi jangka panjang / AIP / DIP | acuan bila dibutuhkan |
| ISO 27001:2022, ISO 22301:2019 | keamanan & business continuity | manajemen kontrol dan ketahanan | acuan desain, bukan klaim sertifikasi |

**PENTING:** tidak berlaku `retensi semua arsip = 10 tahun`. Regulasi sektoral, jadwal retensi arsip yang disahkan Bank, dasar hukum dan nilai guna, hukum terkait pajak/kredit/AML/audit/litigasi, dan status permanen harus dikaji per seri arsip. Kewajiban spesifik, pengecualian, serta applicability per jenis bank memerlukan legal mapping pasal dan validasi Compliance/Legal Bank. `VERIFY` sebelum mengunci retensi di production.

## 7. Arsitektur sasaran (rekomendasi, belum keputusan stack)
- Frontend: web responsif, peran spesifik, WCAG-aware. Backend: typed APIs, domain services, job queues, policy/retention engine; dapat memakai Next.js/TypeScript jika disetujui TI Bank.
- DB transaksional kuat (mis. PostgreSQL) untuk relasi rekam arsip, legal holds, persetujuan, transaksi lokasi/loan, dan audit.
- Objek file asli & derivatives di object storage dengan encryption, versioning, retention/object lock/WORM sesuai pilihan yang diuji; key & encryption material dikelola KMS/HSM dengan pemisahan tugas.
- Pipeline ingest asynchronous untuk OCR/AV/checksum/validasi; search index boleh menyimpan derivative/redacted data yang tunduk ACL sama. Hasil OCR bukan sumber kebenaran.
- Audit log append-only serta forward ke SIEM; sinkronisasi waktu; backup immutable/out-of-band, restore drill, RPO/RTO disetujui `TBD-BANK`.
- SSO OIDC/SAML via IdP Bank; MFA, SCIM atau provisioning terkendali, RBAC+ABAC, session expiration, privileged/break-glass controls.
- Deployment pilihan on-premises/private/hybrid dengan data residency, hak audit dan exit plan sesuai risk assessment dan persetujuan bank. Jangan default ke layanan public cloud/Free tier untuk arsip rahasia produksi tanpa review regulasi dan kontrak.
- Tenant isolation jika multi-bank: database & object path policies, key separation, negative tests, context injection guard.
- Logs dan telemetri tidak boleh mengandung isi dokumen, identitas sensitif, token, atau kunci.

## 8. AI/OCR: model akurat dan bertanggung jawab
- OCR/scanned image preprocessing dengan kemampuan Bahasa Indonesia; simpan file asli, hasil OCR sebagai derivative terpisah + lokasi bounding box.
- AI untuk **usulan** metadata, seri, kode klasifikasi, duplikat potensial, ringkasan, normalisasi nama, pencarian semantik. Selalu tampilkan confidence & alasan/evidence span, versi model/prompt, timestamp, manual override history.
- Lapisan deterministic rules untuk retention, approval, data access, hold, disposisi. **LLM tidak memutuskan retensi dan tidak menghapus arsip.**
- Benchmark dataset berlabel dari Bank (redacted), per kelas record, confusion matrix/precision/recall, false negative kategori kritikal, OCR character/word error rate; threshold disetujui `TBD-BANK`.
- Evaluasi model dan prompt-injection, data leakage, retraining prohibition, vendor/residency check, optional on-prem inference. Konten hasil OCR dan unggahan adalah data tak tepercaya untuk AI agent.

## 9. Roadmap delivery dan gerbang mutu
**WP0 (0–2 minggu, estimasi rencana):** impor baseline jika ada; inventarisasi sampel fiktif; BRD, daftar klasifikasi, JRA & control applicability; ADR; target deployment, RACI, sign-off. Exit: baseline, control matrix, data classification dan UAT P0 disetujui.
**WP1 (minggu 3–6):** platform identity, schema, case files, metadata, ingest, blob immutability, checksum, audit/event ledger, CI/secret scanning. Exit: negative RBAC/tenant/immutable tests lulus.
**WP2 (minggu 7–10):** retention event engine, multi-hold, eligibility, 4-eyes disposal, BA, audit exports, privacy & legal exception; physical archive baseline. Exit: test unauthorized/maker-self-approve/hold blocks disposal.
**WP3 (minggu 11–14):** search ACL, OCR/QC, physical chain of custody, systems integration mock, preservation & backfill. Exit: indexing and search do not leak data outside privileges.
**WP4 (minggu 15–18):** security hardening, migration, performance, SIEM, VA/PT, backup/restore/DR exercise, SOP, training, UAT evidence. Exit: all release gates pass.
**WP5 (minggu 19–20):** controlled rollout, monitoring, hypercare, regulatory evidence pack, rollback plan, ownership transfer. Exit: formal go-live acceptance by Bank.

Durasi adalah ilustrasi untuk perencanaan; perlu baseline kompleksitas arsip, jumlah cabang, volume data, sistem sumber dan procurement.

## 10. Acceptance tests wajib sebelum produksi
1. Record declared tidak bisa di-overwrite meskipun oleh admin aplikasi; versi baru mempertahankan seluruh provenance.
2. SHA-256 sama untuk objek asli setelah retrieve/export/restore; corruption detection & alert diuji.
3. Cross-unit dan cross-tenant search, preview, signed URL, API, export menghasilkan DENY tanpa privilege.
4. Administrator sistem tidak dapat menyetujui pemusnahan sendiri dan menghapus audit trail.
5. JRA per seri memakai trigger awal yang benar, bukan tanggal upload.
6. Hold yang dipasang sebelum maupun saat batch dispose memblokir job, termasuk retry/race condition.
7. Legal hold tidak bisa dilepas tanpa approver yang berhak; perubahan dicatat.
8. Jadwal retensi lama/baru, efektif date dan exception diproses deterministik dan repeatable.
9. BA pemusnahan mencakup identitas daftar item, approval, metode, pelaksana, waktu, hash manifest, status replicas/derivatives.
10. Permintaan hak PDP diverifikasi terhadap konflik retensi wajib dan redaksi/penolakan terekam alasan.
11. Penelusuran barcode mengungkap lokasi, custodian, riwayat transfer, peminjam, keterlambatan dan hasil stock opname.
12. OCR/AI dengan confidence rendah diwajibkan human review; cannot automatically assign disposition.
13. Audit log mencegah modifikasi dan dapat di-reconcile dengan events.
14. Restore dari backup terisolasi berhasil dengan evidence dan target RPO/RTO Bank.
15. Ingest masif terhenti dengan aman bila malware/invalid type/zip bomb; tidak ada untrusted content dieksekusi.
16. Dokumen bertanda tangan elektronik dan material bukti validasi tetap tersedia untuk pembuktian.
17. Penarikan/penyalinan batch ke regulator direkam, dilimit, diberi redaksi sesuai otorisasi.
18. Perubahan role, klasifikasi, JRA dan metadata schema memiliki maker-checker/audit.
19. Data arsip yang dideklarasikan tetap dapat diekspor ke format terbuka beserta metadata/provenance tanpa bergantung pada vendor.
20. UAT seluruh proses bank terhadap kasus kredit, keuangan, HR, hukum, korespondensi, kontrak, fisik, permanen dan sengketa.

## 11. Backlog dan deliverables P0/P1/P2
**P0 sebelum pilot bermakna:** BRD & matriks aturan, penetapan risk owner, desain keamanan & arsitektur, schema/meta, SSO/RBAC, capture/declaration, immutability, audit, retention, legal hold, disposisi, backup/restore, tests & CI.
**P1 sebelum ekspansi cabang:** physical custody, pencarian aman, metadata mass edit kontroll, e-signature, format migration, transfer, integrasi core, reporting regulator, DR.
**P2 optimisasi:** AI OCR advanced, semantic search, automated suggestions, analytics, capacity prediction, anomaly alerts. P2 tidak memblokir kemampuan dasar menjadi sistem records.

## 12. Keputusan perlu disetujui Bank sebelum build
- Bentuk hukum bank dan lingkup aturan: BUMD/BUS/UUS/BPR/BPRS, cakupan kantor, kepatuhan JRA.
- Daftar record series dan JRA definitif (jenis, trigger, nilai guna, basis hukum, review/approver).
- Kategori arsip rahasia & klasifikasi informasi dan kebijakan akses per unit/cabang.
- Alur approval, retensi fisik asli vs digital, legal hold, transfer, pemusnahan.
- Sistem sumber dan pola integrasi; volume, ukuran, SLA, RPO/RTO, WORM & kebutuhan preservasi.
- Data residency, pemrosesan AI/on-prem/cloud, third-party risk, data sharing, DPA, DPIA.
- Pengguna, approval matrix, tanggung jawab Records Officer, Legal, Compliance, DPO, IT, Audit.

## 13. Rujukan tepercaya yang diverifikasi
- UU 43/2009: https://peraturan.bpk.go.id/Details/38788/uu-no-43-tahun-2009
- PP 28/2012: https://peraturan.bpk.go.id/Details/5240/pp-no-28-tahun-2012
- Peraturan ANRI 6/2021: https://jdih.anri.go.id/peraturan/peraturan-arsip-nasional-republik-indonesia-no-6-tahun-2021
- UU 8/1997: https://peraturan.bpk.go.id/Details/45929/uu-no-8-tahun-1997
- PP 87/1999: https://peraturan.bpk.go.id/Details/54595/pp-no-87-tahun-1999
- PP 88/1999: https://peraturan.bpk.go.id/Details/54598/pp-no-88-tahun-1999
- UU ITE UU 1/2024: https://jdih.komdigi.go.id/produk_hukum/view/id/884/t/undangundang%20nomor%201%20tahun%202024
- PP 71/2019: https://peraturan.bpk.go.id/Details/122030/pp-no-71-
- UU PDP 27/2022: https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/
- POJK 11/2022: https://peraturan.bpk.go.id/Details/227376/peraturan-ojk-no-11pojk032022-tahun-2022
- PADK OJK 1/2026: https://ojk.go.id/id/regulasi/Pages/PADK-1-Tahun-2026-Penyelenggaraan-Teknologi-Informasi-oleh-Bank-Umum.aspx
- SEOJK 29/2022: https://ojk.go.id/id/regulasi/Pages/Ketahanan-dan-Keamanan-Siber-Bagi-Bank-Umum.aspx
- POJK 8/2023: https://ojk.go.id/id/regulasi/Pages/POJK-APU-PPT-dan-PPPSPM-di-SJK.aspx
- ISO 15489-1:2016: https://www.iso.org/standard/62542.html
- ISO 16175-1:2020: https://www.iso.org/standard/74294.html
- ISO/TS 16175-2:2020: https://www.iso.org/standard/74293.html
- ISO 23081-1:2017: https://www.iso.org/standard/73172.html
- ISO 14721:2025: https://www.iso.org/standard/87471.html

**GATE:** sebelum produksi, Legal/Compliance dan Records Officer bank harus menandatangani matriks peraturan yang mencantumkan pasal yang tepat, applicability, parameter implementasi, control owner, bukti dan hasil UAT.
