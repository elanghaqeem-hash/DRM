# Verified GitHub Baseline — EDARMS WP0, 30 October 2026

## Repository observations at inspection
- Main HEAD: 4a8f07ecd1a8368d91d8bdaa2ca281330dd89bdb — master prompt and preliminary enterprise audit, documentation only.
- Existing feature/sprint0-foundation HEAD: 02555dff4f7d6a360b2e03fe373d48873e70a053 — Python 3.12/FastAPI, PostgreSQL 16, OIDC Keycloak, Docker Compose, MinIO, Redis, initial Alembic migration, audit chain, domain unit tests and GitHub CI.
- Branches diverged (feature ahead 2, behind main 5); draft [PR #1](https://github.com/elanghaqeem-hash/DRM/pull/1). Chosen execution branch preserves feature code and imports main's master and audit docs; no destructive merge or force-push.
- Latest inspected [GitHub workflow run](https://github.com/elanghaqeem-hash/DRM/actions/runs/41007380254): PostgreSQL integration job SUCCESS; quality job FAILURE at Gitleaks because shallow checkout lacks requested revision range; 0 bytes scanned. No confirmed clean secret scan. Remediate with full history, keep scanner.
- Production not deployed/verified; no real Bank data, signed JRA, external WORM audit, KMS/AV/restore or independent security tests.

## Evidence-led gaps
| Finding | Severity | Treatment |
|---|---|---|
| Legacy record/audit tables have no tenant_id or scoped row security | P0 | NOT SAFE for real multi-bank data. Separate isolated PoC task slice; retrofit in WP2–WP3 |
| Bank IAM federation/MFA, session lifecycle and ABAC missing | P0 | WP1 partial, Bank IdP TBD |
| No UI implementation (apps/web has README only) | P0 | WP1 onward |
| No ingest, immutable object store, AV, OCR | P0 | WP3/WP7 |
| No approved JRA/hold/disposal execution | P0 | WP4 blocked by Bank policy |
| External WORM audit/backup/restore/DR unverified | P0 | WP6/WP8 |
| Main master prompt not present on feature ancestor | P0 docs | Imported without overwriting PoC code |
| CI partial secret scan | P0 | Full Git checkout before Gitleaks |

## WP0 outputs and gate
BRD draft, control matrix, conceptual ERD, 62-submenu/414-action registry, 330-slot UAT skeleton, ADR and decision log are deliverables for review. They are **not accepted Bank policies or completed UI**. WP0 technical inventory done; business/legal gate remains BLOCKED until Bank reviews the 20 TBD-BANK controls and signs off RACI, architecture, acceptance and legal applicability. Continue safe synthetic PoC only.
