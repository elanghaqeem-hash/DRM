"""Explicit Bank-owned AV and private WORM S3 configuration.

Install optional storage extra. Never connect to external AI, AV or S3
without approved network/residency and KMS parameters.
"""
import os
from urllib.parse import urlsplit

from services.records.secure_ingest import (
    ClamAVInstream, IngestBlocked, S3ImmutableOriginalStore,
)


def configured_pipeline(settings=None):
    cfg = os.environ if settings is None else settings
    mandatory = (
        "EDARMS_AV_HOST", "EDARMS_AV_PORT", "EDARMS_S3_ENDPOINT",
        "EDARMS_S3_REGION", "EDARMS_WORM_BUCKET", "EDARMS_KMS_KEY_ID",
        "EDARMS_MAX_FILE_BYTES",
    )
    if any(not cfg.get(key) for key in mandatory):
        raise IngestBlocked("Incomplete Bank-approved AV/WORM/KMS parameters")
    endpoint = urlsplit(cfg["EDARMS_S3_ENDPOINT"])
    if endpoint.scheme != "https" and not (
        endpoint.scheme == "http" and endpoint.hostname in ("localhost", "127.0.0.1")
    ):
        raise IngestBlocked("S3 endpoint must use TLS except loopback PoC")
    try:
        max_bytes = int(cfg["EDARMS_MAX_FILE_BYTES"])
        port = int(cfg["EDARMS_AV_PORT"])
    except ValueError as exc:
        raise IngestBlocked("Invalid AV port or Bank-approved file size") from exc
    if max_bytes <= 0 or max_bytes > 2 ** 31:
        raise IngestBlocked("Invalid file size limit")
    try:
        import boto3
    except ImportError as exc:
        raise IngestBlocked("Install approved S3 SDK: storage optional extra") from exc
    client = boto3.client(
        "s3", endpoint_url=cfg["EDARMS_S3_ENDPOINT"],
        region_name=cfg["EDARMS_S3_REGION"],
    )
    scanner = ClamAVInstream(cfg["EDARMS_AV_HOST"], port)
    storage = S3ImmutableOriginalStore(
        client, cfg["EDARMS_WORM_BUCKET"], cfg["EDARMS_KMS_KEY_ID"]
    )
    return scanner, storage, max_bytes
