"""Report unidentified historical archive rows without exposing record contents.

Run with migration-owner credentials in an approved administrative environment.
This never infers or writes tenant identifiers.
"""
import json
import os
import psycopg

LEGACY = (
    "classification_scheme", "retention_rule", "record_class", "aggregation",
    "record", "record_aggregation", "record_version", "physical_location",
    "physical_item", "loan", "legal_hold", "legal_hold_scope",
    "disposition_batch", "disposition_item", "disposition_certificate",
    "access_request", "pdp_processing_register", "data_subject_request",
    "role", "permission", "role_permission", "user_attribute",
    "access_review_campaign", "audit_event",
)


def main():
    result = {}
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        role = conn.execute(
            "SELECT rolsuper FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if not role or not role[0]:
            raise SystemExit("Privileged migration operator required for quarantine report")
        for table in LEGACY:
            # The table names are hard-coded above; no user-provided SQL.
            total, unknown = conn.execute(
                f"SELECT count(*), count(*) FILTER (WHERE tenant_id IS NULL) FROM {table}"
            ).fetchone()
            result[table] = {"total": total, "unmapped_quarantined": unknown}
    unresolved = sum(value["unmapped_quarantined"] for value in result.values())
    print(json.dumps({"tables": result, "unmapped_rows": unresolved,
                      "backfill_status": "BLOCKED" if unresolved else "NO_UNMAPPED_ROWS"},
                     sort_keys=True, indent=2))
    if unresolved:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
