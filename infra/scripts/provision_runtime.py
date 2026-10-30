"""Provision a separate NO-BYPASSRLS application identity after PoC migrations.

Run ONLY with the migration admin DSN; never expose that DSN in the API
container. Passwords are generated in the ignored local .env, not committed.
"""
import os
import psycopg
from psycopg import sql


def provision():
    admin_url = os.environ.get("DATABASE_URL")
    name = os.environ.get("APP_DB_USER")
    password = os.environ.get("APP_DB_PASSWORD")
    if not admin_url or not name or not password or len(password) < 24:
        raise RuntimeError("Migration DSN and strong isolated app credentials required")
    if name == os.environ.get("POSTGRES_USER"):
        raise RuntimeError("Application role must differ from database migration owner")
    if not name.replace("_", "").isalnum() or not name[0].isalpha():
        raise RuntimeError("Invalid database role identifier")
    with psycopg.connect(admin_url, autocommit=True) as conn:
        role = conn.execute(
            "SELECT rolsuper,rolbypassrls,rolcreatedb,rolcreaterole "
            "FROM pg_roles WHERE rolname=%s", (name,)
        ).fetchone()
        if role and any(role):
            raise RuntimeError("Existing application role has unsafe privileges")
        if role is None:
            conn.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER "
                    "NOBYPASSRLS NOCREATEDB NOCREATEROLE"
                ).format(sql.Identifier(name), sql.Literal(password))
            )
        else:
            conn.execute(
                sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {}").format(
                    sql.Identifier(name), sql.Literal(password)
                )
            )
        role_id = sql.Identifier(name)
        conn.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(role_id))
        # SELECT is filtered by FORCE RLS on all archive tables.
        conn.execute(sql.SQL(
            "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {}"
        ).format(role_id))
        for table in (
            "edarms_review_task", "edarms_task_event",
            "edarms_archive_control_event", "legal_hold",
            "legal_hold_scope", "edarms_legal_hold_event",
        ):
            conn.execute(
                sql.SQL("GRANT INSERT ON {} TO {}").format(
                    sql.Identifier(table), role_id
                )
            )
        for table in ("edarms_review_task", "legal_hold"):
            conn.execute(sql.SQL("GRANT UPDATE ON {} TO {}").format(
                sql.Identifier(table), role_id
            ))
        conn.execute(sql.SQL(
            "GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO {}"
        ).format(role_id))
        role = conn.execute(
            "SELECT rolsuper,rolbypassrls,rolcreatedb,rolcreaterole "
            "FROM pg_roles WHERE rolname=%s", (name,)
        ).fetchone()
        if role != (False, False, False, False):
            raise RuntimeError("App role privilege verification failed")
    print("Non-privileged, tenant-scoped PoC DB runtime role ready (no secrets logged).")


if __name__ == "__main__":
    provision()
