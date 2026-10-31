"""Fail-closed ClamAV INSTREAM and S3 Object Lock compliance pipeline.

Library integration only: NOT exposed as a records upload API without
Bank-approved JRA, tenant ownership and real security/UAT evidence.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import socket
import struct
from uuid import UUID, uuid4


class IngestRejected(RuntimeError):
    """Ingestion is denied; callers must not release the file."""


class MalwareDetected(IngestRejected):
    pass


@dataclass(frozen=True)
class ImmutableReceipt:
    tenant_id: str
    record_id: str
    object_key: str
    version_id: str
    sha256: str
    retain_until: datetime


class ClamAVScanner:
    def __init__(self, host: str, port: int = 3310, timeout: float = 10,
                 max_bytes: int = 64 * 1024 * 1024):
        self.host, self.port, self.timeout, self.max_bytes = (
            host, port, timeout, max_bytes
        )

    def scan(self, content: bytes) -> None:
        if not isinstance(content, bytes) or not content or len(content) > self.max_bytes:
            raise IngestRejected("Empty or oversized content")
        try:
            with socket.create_connection(
                (self.host, self.port), timeout=self.timeout
            ) as sock:
                sock.settimeout(self.timeout)
                sock.sendall(b"zINSTREAM\x00")
                for offset in range(0, len(content), 1024 * 1024):
                    chunk = content[offset:offset + 1024 * 1024]
                    sock.sendall(struct.pack("!I", len(chunk)) + chunk)
                sock.sendall(struct.pack("!I", 0))
                answer = sock.recv(2048)
        except (OSError, TimeoutError) as exc:
            raise IngestRejected("Antivirus not available: file quarantined") from exc
        if b"FOUND" in answer:
            raise MalwareDetected("Malware detected: file quarantined")
        if answer.rstrip(b"\x00\r\n").endswith(b": OK"):
            return
        raise IngestRejected("Unverified antivirus verdict: file quarantined")


class S3ObjectLockStore:
    """Uses S3-compatible boto3 client with Object Lock compliance mode.

    Bucket MUST have Object Lock enabled at creation; no silent fallback.
    """

    def __init__(self, client, bucket: str):
        if not bucket:
            raise IngestRejected("Immutable bucket is not configured")
        self.client, self.bucket = client, bucket

    def put_immutable(self, *, content: bytes, tenant_id: UUID,
                      record_id: UUID, retain_until: datetime,
                      scanner: ClamAVScanner) -> ImmutableReceipt:
        if not isinstance(retain_until, datetime) or retain_until.tzinfo is None:
            raise IngestRejected("Retention deadline must be timezone-aware")
        if retain_until <= datetime.now(timezone.utc):
            raise IngestRejected("Retention must be approved and in the future")
        # MALWARE SCANNING precedes any externally addressable object write.
        scanner.scan(content)
        try:
            configuration = self.client.get_object_lock_configuration(
                Bucket=self.bucket
            )["ObjectLockConfiguration"]
            if configuration.get("ObjectLockEnabled") != "Enabled":
                raise IngestRejected("Object Lock is not enabled on bucket")
            key = f"tenants/{tenant_id}/records/{record_id}/versions/{uuid4().hex}"
            digest = sha256(content).hexdigest()
            uploaded = self.client.put_object(
                Bucket=self.bucket, Key=key, Body=content,
                ObjectLockMode="COMPLIANCE",
                ObjectLockRetainUntilDate=retain_until,
                Metadata={"sha256": digest, "tenant-id": str(tenant_id),
                          "record-id": str(record_id)},
            )
            version = uploaded.get("VersionId")
            if not version:
                raise IngestRejected("Versioned immutable storage not confirmed")
            head = self.client.head_object(
                Bucket=self.bucket, Key=key, VersionId=version
            )
            expiry = head.get("ObjectLockRetainUntilDate")
            if (
                head.get("ObjectLockMode") != "COMPLIANCE"
                or not isinstance(expiry, datetime)
                or expiry < retain_until
                or head.get("Metadata", {}).get("sha256") != digest
                or head.get("Metadata", {}).get("tenant-id") != str(tenant_id)
                or head.get("ContentLength") != len(content)
            ):
                raise IngestRejected("Object lock or checksum verification failed")
            return ImmutableReceipt(
                str(tenant_id), str(record_id), key, version, digest,
                retain_until,
            )
        except IngestRejected:
            raise
        except Exception as exc:
            raise IngestRejected(
                "Object storage failure: record not released"
            ) from exc


def create_s3_store(bucket: str, endpoint_url: str | None = None) -> S3ObjectLockStore:
    """Real S3/MinIO adapter; credentials come from the workload credential chain."""
    import boto3

    client = boto3.client("s3", endpoint_url=endpoint_url)
    return S3ObjectLockStore(client, bucket)
