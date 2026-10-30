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


---

## Existing FastAPI PoC and EDARMS WP0/WP1


**Repository utama:** https://github.com/elanghaqeem-hash/DRM  
**Baseline:** 30 Oktober 2026 | **Implementasi:** Sprint 0 foundation + Sprint 1 domain-rule starter  
**Status:** PROTOTYPE ONLY — tidak untuk produksi, bukan sistem arsip bank operasional.

## Arsitektur

Python 3.12, FastAPI, PostgreSQL 16, Keycloak OIDC, MinIO, Redis, Docker Compose.
Struktur modular disiapkan untuk 14 modul: CAP, MTD, CLS, VER, ACC, WFL, SRC,
LON, PHY, RET, LGH, VIT, AUD, ADM; layanan lintas fungsi PDP dan TPM.

## Yang sudah ada

- Database migration awal (record, class, retention rule, version, loan, hold,
  disposition, ACL, PDP, audit). **Tabel tidak berarti modul bisnis sudah selesai.**
- Authenticated audit write/verify; SHA-256 hash chain dan DB update/delete trigger.
- Auth OIDC token issuer/audience/signature/expiry; PoC Keycloak without seeded users.
- Local-only Docker Compose, migrations, CI quality/integration job, tests.
- Sprint 1 pure domain rules for approved classification, dynamic mandatory metadata,
  maker-checker, and immutable declared records. **Belum terhubung ke API/data/object storage.**
- Traceability and open Bank parameter register; source PED/CTL numbers provisional.

## Cara menjalankan PoC lokal

```bash
python3 infra/scripts/init_env.py
docker compose up --build -d
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
```

API docs: http://127.0.0.1:8000/docs . Keycloak: http://127.0.0.1:8080 .
Create fictitious identities and an OIDC audience mapper for `drm-api`. No
real customer identity, bank document or production data is permitted.

## Validasi

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -m 'not integration' -q
alembic -c infra/alembic.ini upgrade head  # DATABASE_URL required
pytest -m integration -q                      # disposable PostgreSQL only
```

The GitHub CI workflow will provide independent test results. Unless a CI run
is explicitly verified, its status is **NOT RUN / NOT VERIFIED**.

## Keamanan dan release gates

- Database hash chain is **not tamper-proof against a PostgreSQL superuser**.
  External WORM anchor / split custody is required before production.
- The PoC has no operational KMS, immutable object store, Bank IAM federation,
  full ABAC, antivirus/DLP, production MFA/TLS, DR, PSrE, or SOC integration.
- Production startup is blocked in Settings. Do not deploy with real records.
- Required Bank policy values remain `TBD-BANK`; legislation and control
  mappings require Bank Legal and Compliance confirmation.
- Follow `AGENTS.md`, `docs/open-parameters.md` and `docs/RELEASE-GATES.md`.

## Roadmap

Sprint 1: CLS/MTD/CAP/VER with actual secure ingest + version locking.
Sprint 2: ACC/ABAC/SRC. Sprint 3: RET/LGH. Sprint 4: PHY/LON.
Sprint 5: VIT/PDP/ADM/SIEM. Sprint 6: UAT, hardening, DR, exit exports.


## EDARMS Enterprise WP0–WP1 — 2026-10-30

Canonical design: [EDARMS Master Prompt](docs/prompts/MASTER-PROMPT-EDARMS-ENTERPRISE-2026-10-30.md), [verified baseline](docs/audit/2026-10-30-verified-wp0-baseline.md), [BRD draft](docs/BRD/EDARMS-BRD.md), [regulatory VERIFY matrix](docs/regulatory/control-matrix.md), [conceptual ERD](docs/architecture/ERD.md), [62-submenu / 414-button inventory](docs/UX/navigation-and-action-registry.md), [330-slot UAT skeleton](docs/UAT/master-scenarios.md).

WP0: technical inventory recorded; Bank/legal review is PENDING. WP1: tenant + membership + generic approval task schema and append-only events, with PostgreSQL FORCE RLS, idempotency, optimistic version checks, maker-checker and authenticated API. No Bank tenants or real identities seeded.

Actual new API (valid signed OIDC JWT + enabled DB membership required):
- GET /v1/workspace/me?tenant_id=UUID — scoped subject and task abilities.
- GET /v1/workspace/tasks?tenant_id=UUID — tasks made by/assigned to subject.
- POST /v1/workspace/tasks — tenant_id,title,assigned_to and mandatory Idempotency-Key header (8–128 chars).
- POST /v1/workspace/tasks/{id}/decision — tenant_id,decision,expected_version,reason (rejection reason mandatory).

These generic review tasks cannot approve legal holds, record declaration or destruction. API runs against disposable PoC PostgreSQL, and requires manually provisioned synthetic tenant/member fixture and configured test IdP; migration does not create an unsafe default login. Legacy record tables and audit endpoint remain unscoped and **NOT SAFE for real multi-bank records**. No functional enterprise web UI yet, no approved Bank JRA, AV, KMS/WORM, backup restore or production.

Run in synthetic sandbox only: alembic -c infra/alembic.ini upgrade head; pytest -m 'not integration' -q; pytest -m integration -q against disposable DB. Follow [release gates](docs/RELEASE-GATES.md) before any live Bank deployment.
