# ADR — Audit integrity
Status: PoC-only, not production accepted (2026-10-30).

SHA-256 chain with atomic serialized PostgreSQL inserts detects ordinary
modifications. A privileged DBA can rewrite the whole ledger and hash chain
unless independent WORM anchors exist. Production must implement separate
custody of cryptographic checkpoints, Object Lock, long-term retention,
restore verification and a malicious administrator threat test.
