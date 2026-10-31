# Keycloak — Local PoC only

Keycloak start-dev is bound to localhost. No user/real Bank identity is seeded.
Create fictitious service identities; configure client secret, audience mapper
(aud=drm-api) and relevant realm roles. Do not enable password grant.
Production federation with Bank AD/LDAP, MFA and access lifecycle is NOT built.
