# Aturan Agent — DRM

Dokumen ini berlaku untuk semua coding agent/ChatGPT yang melakukan pekerjaan pada proyek **Digital Records Management (DRM)**.

## Repository sumber kebenaran

- GitHub: https://github.com/elanghaqeem-hash/DRM
- Default branch: `main`.
- GitHub adalah sumber kebenaran implementasi; pesan chat hanyalah instruksi dan diskusi, bukan bukti perubahan kode berhasil disimpan.
- Baca `README.md`, `AGENTS.md`, `CHANGELOG.md`, serta kondisi branch, berkas, dan perubahan terbaru sebelum memulai pekerjaan.
- Konfirmasi scope dan dampak pekerjaan terhadap fitur yang sudah ada; pertahankan kompatibilitas kecuali ada instruksi perubahan yang jelas.

## Siklus kerja wajib per permintaan perubahan

1. **Inspect** — baca kode, versi terbaru dan test yang ada. Jangan membuat struktur proyek duplikat.
2. **Plan** — identifikasi berkas terdampak, kriteria selesai, dependensi, risiko, dan kebutuhan migrasi.
3. **Implement** — ubah artefak di repository, bukan hanya memaparkan kode dalam jawaban chat.
4. **Verify** — jalankan uji yang relevan bila runtime tersedia; bila tidak dapat dijalankan, nyatakan dengan jelas status `NOT RUN`.
5. **Commit** — buat commit GitHub yang jelas, singkat dan dapat diaudit; untuk perubahan kompleks/berisiko gunakan branch kerja dan PR.
6. **Report** — berikan SHA commit, branch, ringkasan berkas, hasil tes, dan tautan PR/commit. Jika gagal, nyatakan penyebabnya tanpa mengklaim berhasil.

## Aturan commit dan perubahan

- Gunakan pesan commit, misalnya `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `chore: ...`.
- Perubahan kecil/terverifikasi dapat diarahkan ke `main`. Perubahan besar atau belum lengkap menggunakan branch `feature/<topik>` atau `fix/<topik>` dan PR.
- Hindari force push dan jangan menghapus riwayat commit.
- Jangan mengubah berkas yang sama secara bersamaan tanpa membaca SHA terkini dan mengendalikan konflik.
- Masukkan catatan perubahan signifikan ke `CHANGELOG.md`. Simpan keputusan sistemik di `docs/decision-log.md`.
- Jangan klaim produksi sudah aktif kecuali deploy dan smoke test aktual terverifikasi.

## Kualitas, keamanan, dan kepatuhan

- Tidak boleh memasukkan credential, token, secret, data nasabah, data karyawan sensitif, ataupun file `.env` ke GitHub.
- Bila aplikasi sudah tersedia, setiap fitur penting perlu validasi input, autentikasi, otorisasi/RBAC, audit trail, pemeriksaan akses lintas organisasi, dan pengujian negatif.
- Terapkan traceability kebutuhan -> rancangan -> kode -> uji -> hasil UAT.
- Parameter spesifik bank yang belum ditetapkan diberi label `TBD-BANK`; interpretasi ketentuan yang belum diverifikasi diberi label `VERIFY`.
- Pertimbangkan tata kelola siklus hidup arsip: penciptaan/penerimaan, klasifikasi, metadata, penelusuran, penyimpanan, retensi, legal hold, transfer, disposisi, dan pemulihan.

## Batas otomatisasi

Aturan ini bersifat *repository guidance*, bukan webhook dari seluruh chat pengguna. Tidak ada jaminan bahwa pesan di luar sesi pengembangan yang mengakses GitHub akan langsung menjadi commit. Agent wajib melakukan tool write/commit yang nyata; jika tidak ada akses GitHub pada sesi tersebut, sediakan patch atau PR-ready changes dan sampaikan bahwa perubahan **belum tersinkron**.

## Prioritas proyek

1. Integritas dan keamanan data serta pemisahan akses.
2. Kebenaran proses bisnis, kepatuhan, dan keterlacakan.
3. Kualitas kode, pengujian, dan kesiapan operasional.
4. Kemudahan penggunaan dan dokumentasi.
