"""Fail-closed ClamAV and S3 Object Lock tests using synthetic bytes."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import socket
import pytest
from services.storage.immutable_ingest import (
    ClamAVScanner, IngestRejected, MalwareDetected, S3ObjectLockStore,
)


class FakeSocket:
    def __init__(self, verdict):
        self.verdict, self.sent = verdict, []
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def settimeout(self, *_):
        pass
    def sendall(self, content):
        self.sent.append(content)
    def recv(self, *_):
        return self.verdict


class FakeS3:
    def __init__(self, lock=True, tamper=False):
        self.lock, self.tamper, self.written = lock, tamper, None
    def get_object_lock_configuration(self, **_):
        return {"ObjectLockConfiguration": {
            "ObjectLockEnabled": "Enabled" if self.lock else "Disabled"
        }}
    def put_object(self, **data):
        self.written = data
        return {"VersionId": "synthetic-v1"}
    def head_object(self, **_):
        data = self.written
        return {
            "ObjectLockMode": "GOVERNANCE" if self.tamper else data["ObjectLockMode"],
            "ObjectLockRetainUntilDate": data["ObjectLockRetainUntilDate"],
            "Metadata": data["Metadata"],
            "ContentLength": len(data["Body"]),
        }


def test_clamav_negative_and_positive(monkeypatch):
    sockets = []
    def fake_connection(*_args, **_kwargs):
        sock = FakeSocket(b"stream: OK\x00")
        sockets.append(sock)
        return sock
    monkeypatch.setattr(socket, "create_connection", fake_connection)
    scanner = ClamAVScanner("127.0.0.1")
    scanner.scan(b"synthetic safe bytes")
    assert sockets[0].sent[0] == b"zINSTREAM\x00"
    assert sockets[0].sent[-1] == b"\x00\x00\x00\x00"

    monkeypatch.setattr(
        socket, "create_connection",
        lambda *_args, **_kwargs: FakeSocket(b"stream: Eicar-Test FOUND\x00"),
    )
    with pytest.raises(MalwareDetected):
        scanner.scan(b"synthetic malware fixture")

    def no_service(*_args, **_kwargs):
        raise OSError("Connection refused")
    monkeypatch.setattr(socket, "create_connection", no_service)
    with pytest.raises(IngestRejected, match="not available"):
        scanner.scan(b"unscanned bytes")
    with pytest.raises(IngestRejected, match="Empty"):
        scanner.scan(b"")


def test_object_lock_receipt_and_failing_closed():
    class ApprovedScanner:
        calls = 0
        def scan(self, content):
            self.calls += 1
            assert content == b"test content"

    expiry = datetime.now(timezone.utc) + timedelta(days=31)
    scanner = ApprovedScanner()
    fake = FakeS3()
    store = S3ObjectLockStore(fake, "synthetic-locked-bucket")
    a, rec = uuid4(), uuid4()
    receipt = store.put_immutable(
        content=b"test content", tenant_id=a, record_id=rec,
        retain_until=expiry, scanner=scanner,
    )
    assert receipt.version_id == "synthetic-v1"
    assert str(a) in receipt.object_key
    assert fake.written["ObjectLockMode"] == "COMPLIANCE"
    assert receipt.sha256 == fake.written["Metadata"]["sha256"]
    assert scanner.calls == 1

    for invalid_store in (FakeS3(lock=False), FakeS3(tamper=True)):
        with pytest.raises(IngestRejected):
            S3ObjectLockStore(invalid_store, "synthetic").put_immutable(
                content=b"test content", tenant_id=a, record_id=rec,
                retain_until=expiry, scanner=scanner,
            )
    with pytest.raises(IngestRejected, match="Retention"):
        store.put_immutable(
            content=b"test content", tenant_id=a, record_id=rec,
            retain_until=datetime.now(timezone.utc) - timedelta(days=1),
            scanner=scanner,
        )


def test_malware_never_reaches_object_storage():
    class RejectScanner:
        def scan(self, _):
            raise MalwareDetected("Positive detection")
    fake = FakeS3()
    with pytest.raises(MalwareDetected):
        S3ObjectLockStore(fake, "synthetic").put_immutable(
            content=b"test content", tenant_id=uuid4(), record_id=uuid4(),
            retain_until=datetime.now(timezone.utc) + timedelta(days=1),
            scanner=RejectScanner(),
        )
    assert fake.written is None
