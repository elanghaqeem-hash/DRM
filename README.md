# Digital Records Management (DRM) Bank — PoC

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
