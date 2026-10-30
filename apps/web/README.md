# EDARMS WP1 — connected browser workspace (PoC only)

This is a **working API-connected generic task inbox**, not a demo with static records, and not the full 62-submenu enterprise product.

## Implemented
- FastAPI serves `/app` and static local assets `/static/edarms.{js,css}` with restrictive CSP and no-store headers.
- Browser OIDC Authorization Code + PKCE S256 using public `drm-web` Keycloak client; access token kept in memory and not written to localStorage. Identity and role/tenant membership established by API.
- Real `/v1/workspace/me`, tenant-scoped task listing, create with idempotency key and human approval/reject with reason; errors displayed; no synthetic KPI values.
- Left sidebar collapses on desktop and becomes mobile drawer. Only task inbox is clickable; unreleased groups are explicitly marked roadmap with no dead links.
- Native accessible labels/focus, skip navigation, mobile cards; no user-controlled innerHTML.
- User-facing logout clears in-memory token and tries Keycloak end-session, but **server-wide token/session revocation is not yet implemented**, hence not production approved.

## Synthetic-only setup
1. Use the existing local Compose stack, migrate Alembic to head, and import Keycloak realm with the `drm-web` public client; configure OIDC audience and trust realm issuer.
2. Open `http://127.0.0.1:8000/app`; log in through Keycloak test identity.
3. Provide the UUID of a **synthetic tenant** with explicitly enabled `edarms_membership` for that subject. Do not add real Bank user/accounts/documents.
4. Use a second authorized synthetic subject with `approver` or `records_manager` membership for reviewer tasks. Creator cannot approve themselves.

Keycloak realm JSON is a **fresh local PoC import**. Existing Keycloak realms are not automatically patched when the JSON file changes; recreate isolated local realm or apply reviewed IdP change. HTTP is allowed on loopback for PoC only. Identity Federation/MFA, tenant provisioning, session revocation, end-to-end browser/Android UAT and Bank branding approvals remain pending.

## Testing
CI: `node --check apps/web/edarms.js`; `python -m json.tool infra/keycloak/drm-poc-realm.json`; `tests/unit/test_workspace_ui.py`; PostgreSQL integration `tests/integration/test_workspace_tasks.py`. Only claim PASS after GitHub run verified. No Playwright or browser OIDC live-flow test yet.
