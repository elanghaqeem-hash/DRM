"""Security-negative tests for AV, WORM, MIME, KMS and read-back fixity."""
from datetime import datetime, timedelta, timezone
from io import BytesIO

import pytest
from services.records.secure_ingest import (
    ClamAVInstream, IngestBlocked, S3ImmutableOriginalStore, capture_original,
)


class FakeScanner:
    def __init__(self, clean=True):
        self.clean = clean
        self.calls = 0

    def scan(self, payload):
        self.calls += 1
        if not self.clean:
            raise IngestBlocked("Malware detected")


class LockedFakeS3:
    def __init__(self, mode="COMPLIANCE", tampered=False):
        self.mode = mode
        self.tampered = tampered
        self.put_calls = 0
        self.content = None

    def get_bucket_versioning(self, **kwargs):
        return {"Status": "Enabled"}

    def get_object_lock_configuration(self, **kwargs):
        return {"ObjectLockConfiguration": {
            "ObjectLockEnabled": "Enabled",
            "Rule": {"DefaultRetention": {"Mode": self.mode, "Days": 1}},
        }}

    def get_public_access_block(self, **kwargs):
        return {"PublicAccessBlockConfiguration": {
            x: True for x in (
                "BlockPublicAcls", "IgnorePublicAcls",
                "BlockPublicPolicy", "RestrictPublicBuckets",
            )
        }}

    def get_bucket_encryption(self, **kwargs):
        return {"ServerSideEncryptionConfiguration": {
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]
        }}

    def put_object(self, **kwargs):
        self.put_calls += 1
        self.content = kwargs["Body"]
        return {"VersionId": "version-synthetic"}

    def head_object(self, **kwargs):
        return {
            "ObjectLockMode": self.mode,
            "ObjectLockRetainUntilDate": datetime.now(timezone.utc) + timedelta(days=1),
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": "synthetic-kms-id",
            "ContentLength": len(self.content),
        }

    def get_object(self, **kwargs):
        return {"Body": BytesIO(self.content + (b"X" if self.tampered else b""))}


PDF = b"%PDF-1.7\nSANDBOX ONLY"


def storage(client):
    return S3ImmutableOriginalStore(client, "synthetic-private", "synthetic-kms-id")


def test_clean_immutable_capture_requires_read_back():
    fake = LockedFakeS3()
    result = capture_original(PDF, "application/pdf", FakeScanner(), storage(fake), 1000)
    assert result.sha256_hex
    assert result.antivirus == "CLAMAV_CLEAN"
    assert result.storage_mode == "S3_OBJECT_LOCK_COMPLIANCE"
    assert fake.put_calls == 1


def test_malware_never_uploaded():
    fake = LockedFakeS3()
    with pytest.raises(IngestBlocked, match="Malware"):
        capture_original(PDF, "application/pdf", FakeScanner(clean=False),
                         storage(fake), 1000)
    assert fake.put_calls == 0


def test_invalid_mime_rejected_without_scan():
    av = FakeScanner()
    with pytest.raises(IngestBlocked, match="MIME"):
        capture_original(PDF, "image/png", av, storage(LockedFakeS3()), 1000)
    assert av.calls == 0


def test_unlocked_storage_rejected_before_scan():
    av = FakeScanner()
    with pytest.raises(IngestBlocked, match="Object Lock"):
        capture_original(PDF, "application/pdf", av, storage(LockedFakeS3("GOVERNANCE")), 1000)
    assert av.calls == 0


def test_corrupted_storage_read_back_rejected():
    with pytest.raises(IngestBlocked, match="fixity"):
        capture_original(PDF, "application/pdf", FakeScanner(),
                         storage(LockedFakeS3(tampered=True)), 1000)


def test_size_limit_fail_closed():
    with pytest.raises(IngestBlocked, match="exceeds"):
        capture_original(PDF, "application/pdf", FakeScanner(), storage(LockedFakeS3()), 2)


def test_no_default_bucket_or_kms():
    with pytest.raises(IngestBlocked, match="KMS"):
        S3ImmutableOriginalStore(LockedFakeS3(), "", "")


def test_av_endpoint_must_be_configured():
    with pytest.raises(ValueError):
        ClamAVInstream("", 0)
