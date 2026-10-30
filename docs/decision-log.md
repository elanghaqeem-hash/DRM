# Decision Log — DRM

Catat keputusan teknis dan bisnis dengan nomor unik, tanggal, status, alternatif, alasan, dampak, dan referensi commit.

## ADR-0001 — GitHub sebagai single source of truth

- **Tanggal:** 2026-10-30
- **Status:** Accepted
- **Keputusan:** Repository `elanghaqeem-hash/DRM` menjadi lokasi utama semua artefak implementasi DRM. Output pengembangan ChatGPT/agent yang berbentuk perubahan artefak wajib dikomit ke repository pada sesi kerja yang mempunyai akses.
- **Alasan:** Menjaga histori revisi, keterlacakan, kolaborasi, dan menghindari hasil perubahan terpecah di berbagai percakapan.
- **Dampak:** Setiap perubahan harus memiliki commit SHA dan laporan status tes. ChatGPT tidak otomatis menyinkronkan seluruh percakapan; push hanya terjadi ketika agent menjalankan perubahan GitHub secara eksplisit.
- **Referensi:** README.md dan AGENTS.md.

## ADR-0002 — Pembatasan baseline dan deployment

- **Tanggal:** 2026-10-30
- **Status:** Proposed
- **Keputusan sementara:** Stack aplikasi, skema database, environment, dan pipeline deployment ditetapkan setelah baseline proyek dapat diperiksa dan kebutuhan bank diverifikasi. Jangan mengklaim aplikasi sudah terbangun atau telah produksi hanya karena repository telah diinisialisasi.
- **Alasan:** Mencegah keputusan arsitektur tanpa bukti dan menghindari deployment yang belum tervalidasi.
- **Tindak lanjut:** Impor kode yang ada bila tersedia, inventarisasi persyaratan, dan susun rencana sprint.
