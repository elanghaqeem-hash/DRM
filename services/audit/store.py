"""PoC audit store: serial append; DB alone does not protect from a DBA."""
from datetime import datetime, timezone
import json
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from services.audit.chain import GENESIS, chain_hash, verify_rows

LEDGER_LOCK_ID = 394102601


def append_event(database_url: str, *, actor_sub: str, actor_role: str,
                 source_ip: str | None, device: str | None, action: str,
                 object_ref: str, before_hash: str | None, after_hash: str | None,
                 result: str) -> dict:
    with psycopg.connect(database_url) as conn:
        with conn.transaction():
            conn.execute("SELECT pg_advisory_xact_lock(%s)", (LEDGER_LOCK_ID,))
            row = conn.execute("SELECT event_hash FROM audit_event ORDER BY seq DESC LIMIT 1").fetchone()
            previous = row[0] if row else GENESIS
            payload = {
                "event_id": str(uuid4()), "ts": datetime.now(timezone.utc).isoformat(),
                "actor_sub": actor_sub, "actor_role": actor_role, "source_ip": source_ip,
                "device": device, "action": action, "object_ref": object_ref,
                "before_hash": before_hash, "after_hash": after_hash, "result": result,
            }
            digest = chain_hash(previous, payload)
            seq = conn.execute("""
                INSERT INTO audit_event(event_id,ts,actor_sub,actor_role,source_ip,device,
                  action,object_ref,before_hash,after_hash,result,prev_hash,event_hash,payload)
                VALUES (%(event_id)s,%(ts)s,%(actor_sub)s,%(actor_role)s,%(source_ip)s,
                  %(device)s,%(action)s,%(object_ref)s,%(before_hash)s,%(after_hash)s,
                  %(result)s,%(prev_hash)s,%(digest)s,%(payload)s::jsonb)
                RETURNING seq
            """, {**payload, "prev_hash": previous, "digest": digest,
                  "payload": json.dumps(payload)}).fetchone()[0]
            return {"seq": seq, "event_id": payload["event_id"], "event_hash": digest}


def verify_chain(database_url: str) -> dict:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.transaction():
            conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            rows = conn.execute("""
                SELECT seq,event_id,ts,actor_sub,actor_role,source_ip,device,action,
                       object_ref,before_hash,after_hash,result,prev_hash,event_hash,payload
                FROM audit_event ORDER BY seq
            """).fetchall()
    valid, failure = verify_rows(rows)
    return {"valid": valid, "events_checked": len(rows), "failure": failure,
            "head_hash": rows[-1]["event_hash"] if rows else GENESIS,
            "external_anchor_verified": False}
