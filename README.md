# DRM — Digital Records Management untuk Perbankan

Repository resmi dan **single source of truth** untuk pengembangan DRM.

**Pemilik repository:** `elanghaqeem-hash`  
**Branch utama:** `main`  
**Konteks awal:** pengembangan Digital Records Management (DRM) untuk lingkungan perbankan Indonesia berdasarkan kebutuhan tata kelola arsip, SOP, BRD, RFP, dan kontrol keamanan yang disepakati.

## Cara bekerja dengan ChatGPT

1. Setiap permintaan pengembangan DRM harus dimulai dengan membaca status terbaru repository ini sebelum mengubah berkas.
2. Semua hasil kerja **yang berbentuk artefak proyek** (kode, konfigurasi, pengujian, desain teknis, dokumen, dan keputusan implementasi) harus ditulis ke repository melalui konektor GitHub pada sesi yang bersangkutan.
3. Jangan menyatakan perubahan sudah terpusat bila belum ada **commit SHA** dari GitHub. Setiap jawaban yang menyebut perubahan selesai harus mencantumkan file yang berubah, branch, commit SHA, serta status tes/deployment yang benar.
4. Perubahan yang sudah teruji dan berisiko rendah boleh dikomit langsung ke `main` sesuai instruksi pengguna; perubahan besar, berisiko, atau belum tervalidasi dibuat di branch `feature/*` atau `fix/*` dengan pull request.
5. Hindari menimpa commit lain: baca versi terkini, lakukan perubahan sekecil mungkin, dan cek konflik sebelum menulis.
6. Simpan perubahan penting ke `CHANGELOG.md` dan keputusan arsitektur ke `docs/decision-log.md`.
7. Jangan commit rahasia, API key, kredensial, data nasabah asli, atau berkas yang mengandung informasi pribadi tanpa prosedur perlindungan yang sesuai.
8. Deployment produksi memerlukan konfigurasi dan pengujian khusus; keberhasilan push tidak berarti sudah live di produksi.

**Batasan sinkronisasi:** Instruksi ini menjadi pedoman bagi sesi ChatGPT/agent yang membaca repository dan memiliki akses GitHub. Ini **bukan integrasi yang menyalin seluruh isi setiap percakapan secara otomatis**, dan tidak menjalankan push ketika tidak ada sesi/agent yang mengeksekusi perubahan. Setiap sesi baru perlu merujuk repository ini dan mengerjakan commit untuk artefak yang dibuat.

## Status awal

- [x] Repository DRM terverifikasi dapat diakses dengan hak push.
- [x] Repository diinisialisasi sebagai pusat perubahan.
- [ ] Kode aplikasi, pilihan stack, skema database, serta baseline proyek diverifikasi dan diimpor.
- [ ] Modul DRM, kontrol keamanan, migrasi, test suite, dan pipeline CI/CD diimplementasikan bertahap.

## Landasan kebutuhan

- Klasifikasi & metadata arsip, retensi, akses berbasis peran, audit trail, pencarian, disposisi/pemusnahan sesuai persetujuan, legal hold, dan pemulihan bencana.
- Kepatuhan dan standar yang relevan, termasuk ISO 15489 dan ISO 16175, harus dipetakan ke kontrol yang dapat diuji.
- Parameter bank dan ketentuan regulasi yang belum diverifikasi wajib diberi tanda `TBD-BANK` / `VERIFY`; jangan menggantinya dengan angka atau ketentuan rekaan.

Lihat [AGENTS.md](AGENTS.md) untuk aturan operasional agent dan [CHANGELOG.md](CHANGELOG.md) untuk riwayat perubahan.
