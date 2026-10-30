"""Original-file capture with real AV and S3 object-lock prerequisites.

Never publish or declare an object if ClamAV or WORM/fixity checks fail.
The Bank must configure a private Object Lock bucket, KMS and signed JRA.
No live bucket is configured by this source file.
"""
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import secrets
import socket
import struct
from typing import Protocol


class IngestBlocked(RuntimeError):
    """Evidence-preserving failure: no valid archive declaration may follow."""


class Scanner(Protocol):
    def scan(self, content: bytes) -> None: ...


class ClamAVInstream:
    """ClamAV clamd INSTREAM (fail closed; no untrusted scanner verdict bypass)."""

    def __init__(self, host: str, port: int, timeout: float = 10.0):
        if not host or not (1 <= port <= 65535) or timeout <= 0:
            raise ValueError("Valid private AV endpoint required")
        self.host, self.port, self.timeout = host, port, timeout

    def scan(self, content: bytes) -> None:
        try:
            with socket.create_connection(
                (self.host, self.port), timeout=self.timeout
            ) as stream:
                stream.settimeout(self.timeout)
                stream.sendall(b"zINSTREAM\0")
                for start in range(0, len(content), 65536):
                    chunk = content[start:start + 65536]
                    stream.sendall(struct.pack("!I", len(chunk)) + chunk)
                stream.sendall(struct.pack("!I", 0))
                reply = bytearray()
                while len(reply) < 4096:
                    part = stream.recv(4096)
                    if not part:
                        break
                    reply.extend(part)
                    if b"\0" in reply or b"\n" in reply:
                        break
        except (TimeoutError, OSError) as exc:
            raise IngestBlocked("Antivirus scanner unavailable") from exc
        if not reply or not reply.split(b"\0", 1)[0].strip().endswith(b"OK"):
            raise IngestBlocked("Antivirus did not return a clean verdict")


@dataclass(frozen=True)
class OriginalManifest:
    key: str
    version_id: str
    sha256_hex: str
    size_bytes: int
    retention_until: str
    antivirus: str
    storage_mode: str


class S3ImmutableOriginalStore:
    """An injected S3-compatible client with private COMPLIANCE Object Lock."""

    def __init__(self, client, bucket: str, kms_key_id: str):
        if not bucket or not kms_key_id:
            raise IngestBlocked("Approved private bucket and KMS key required")
        self.client = client
        self.bucket = bucket
        self.kms_key_id = kms_key_id

    def preflight(self) -> None:
        try:
            versioning = self.client.get_bucket_versioning(Bucket=self.bucket)
            lock = self.client.get_object_lock_configuration(Bucket=self.bucket)[
                "ObjectLockConfiguration"
            ]
            default = lock.get("Rule", {}).get("DefaultRetention", {})
            public = self.client.get_public_access_block(Bucket=self.bucket)[
                "PublicAccessBlockConfiguration"
            ]
            encrypted = self.client.get_bucket_encryption(Bucket=self.bucket)
        except (KeyError, TypeError, Exception) as exc:
            raise IngestBlocked("Cannot verify private locked encrypted storage") from exc
        if (versioning.get("Status") != "Enabled"
                or lock.get("ObjectLockEnabled") != "Enabled"
                or default.get("Mode") != "COMPLIANCE"
                or not (default.get("Days", 0) > 0 or default.get("Years", 0) > 0)
                or not all(public.get(flag) is True for flag in (
                    "BlockPublicAcls", "IgnorePublicAcls",
                    "BlockPublicPolicy", "RestrictPublicBuckets"
                ))
                or not encrypted.get("ServerSideEncryptionConfiguration", {}).get("Rules")):
            raise IngestBlocked("S3 Object Lock, private ACL and encryption mandatory")

    def store(self, content: bytes, mime: str, hex_digest: str) -> OriginalManifest:
        key = "original/" + secrets.token_hex(24)
        try:
            saved = self.client.put_object(
                Bucket=self.bucket, Key=key, Body=content,
                ContentType=mime,
                ChecksumSHA256=b64encode(bytes.fromhex(hex_digest)).decode("ascii"),
                ServerSideEncryption="aws:kms",
                SSEKMSKeyId=self.kms_key_id,
            )
            version = saved.get("VersionId")
            if not version:
                raise IngestBlocked("Missing object version identifier")
            head = self.client.head_object(
                Bucket=self.bucket, Key=key, VersionId=version
            )
            lock_until = head.get("ObjectLockRetainUntilDate")
            if (head.get("ObjectLockMode") != "COMPLIANCE"
                    or not isinstance(lock_until, datetime)
                    or lock_until <= datetime.now(timezone.utc)
                    or head.get("ServerSideEncryption") != "aws:kms"
                    or head.get("SSEKMSKeyId") != self.kms_key_id
                    or head.get("ContentLength") != len(content)):
                raise IngestBlocked("Original not verifiably locked or encrypted")
            response = self.client.get_object(
                Bucket=self.bucket, Key=key, VersionId=version
            )
            actual = response["Body"].read(len(content) + 1)
            if sha256(actual).hexdigest() != hex_digest:
                raise IngestBlocked("Read-back fixity verification failed")
        except IngestBlocked:
            raise
        except Exception as exc:
            raise IngestBlocked("Immutable store unavailable or failed") from exc
        return OriginalManifest(
            key, version, hex_digest, len(content), lock_until.isoformat(),
            "CLAMAV_CLEAN", "S3_OBJECT_LOCK_COMPLIANCE",
        )


ALLOWED_MIME_MAGIC = {
    "application/pdf": b"%PDF-",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff",
    "image/tiff": b"II*\x00",
}


def capture_original(
    content: bytes, mime: str, scanner: Scanner, store: S3ImmutableOriginalStore,
    max_bytes: int,
) -> OriginalManifest:
    """No metadata/DB declaration until scan+lock+roundtrip hash all succeed."""
    if max_bytes < 1 or not content or len(content) > max_bytes:
        raise IngestBlocked("File empty or exceeds Bank-approved limit")
    header = ALLOWED_MIME_MAGIC.get(mime)
    if header is None or not content.startswith(header):
        raise IngestBlocked("Unsupported or content-mismatched MIME")
    store.preflight()
    scanner.scan(content)
    return store.store(content, mime, sha256(content).hexdigest())
