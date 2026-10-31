"""Provision separate least-privilege PostgreSQL API identity after migrations.

Must only run from the controlled migration/provisioning container, never API.
Requires POSTGRES_RUNTIME_PASSWORD generated locally or injected from a vault.
"""
import os
import psycopg
from psycopg import sql


def main():
    owner_url = os.environ["DATABASE_URL"]
    password = os.environ["POSTGRES_RUNTIME_PASSWORD"]
    if len(password) < 24 or password.startswith("TBD"):
        raise SystemExit("Set a strong runtime password; refusing provisioning")
    with psycopg.connect(owner_url, autocommit=True) as conn:
        # Password value is never logged, concatenated into SQL, or printed.
        found = conn.execute(
            "SELECT 1 FROM pg_roles WHERE rolname='edarms_api_login'"
        ).fetchone()
        if found:
            raise SystemExit("Runtime user already exists; change credentials via secure DBA process")
        conn.execute(
            sql.SQL(
                "CREATE ROLE edarms_api_login LOGIN NOSUPERUSER NOCREATEDB "
                "NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}"
            ).format(sql.Literal(password))
        )
        conn.execute("GRANT edarms_runtime TO edarms_api_login")
        role = conn.execute(
            "SELECT rolsuper, rolbypassrls, rolcanlogin "
            "FROM pg_roles WHERE rolname='edarms_api_login'"
        ).fetchone()
        if role != (False, False, True):
            raise SystemExit("Provisioned identity does not meet RLS safety requirement")
    print("Least-privilege API role provisioned (no secret output).")


if __name__ == "__main__":
    main()
