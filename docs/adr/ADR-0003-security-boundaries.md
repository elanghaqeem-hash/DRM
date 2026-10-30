# ADR — Security and data residency
Status: PoC-only (2026-10-30).

Signed JWT issuer/audience/expiry validation is present. Bank SSO federation,
MFA, SCIM/deprovisioning and ABAC are not. PoC uses HTTP on loopback and
Keycloak start-dev; production use is forbidden. Bank requires all deployed
components and backups in Indonesia, without assuming regulatory exceptions.
