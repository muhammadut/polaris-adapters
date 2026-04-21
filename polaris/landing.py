"""Bronze-layer landing: fetch raw bytes from a URL, store unchanged in Azure Blob.

Single public function: land_raw(source_id, url, ...) -> dict.

Every Phase-1 access test calls this. One function, reused 115 times.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load .env once on module import so every runner script gets creds without ceremony.
load_dotenv()


@dataclass
class LandingResult:
    """Result of one land_raw call. One row in phase1-results.jsonl."""

    source_id: str
    url: str
    ok: bool
    tested_at: str
    http_status: int | None = None
    content_type: str | None = None
    bytes: int | None = None
    blob_path: str | None = None
    error: str | None = None
    error_type: str | None = None
    blocker_type: str | None = None  # auth_required | scraping_needed | ... | None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


def _blob_service_client() -> BlobServiceClient:
    """Build a BlobServiceClient from env-provided service principal creds."""
    tenant_id = os.environ["AZURE_TENANT_ID"]
    client_id = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    storage_account = os.environ["AZURE_STORAGE_ACCOUNT"]

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    account_url = f"https://{storage_account}.blob.core.windows.net"
    return BlobServiceClient(account_url=account_url, credential=credential)


_GENERIC_BASENAMES = {
    "xml", "json", "csv", "html", "pdf", "txt", "rss", "atom",
    "response", "index", "",
}


def _build_blob_path(
    source_id: str,
    url: str,
    ext: str,
    now: datetime,
    basename: str | None = None,
) -> str:
    """polaris-bronze/<source_id>/raw/<YYYY-MM-DD>/<HH-MM-SS>_<basename>.<ext>."""
    date_path = now.strftime("%Y-%m-%d")
    time_part = now.strftime("%H-%M-%S")

    if basename is None:
        url_basename = Path(url.rstrip("/").split("?")[0]).name or ""
        if "." in url_basename:
            url_basename = url_basename.rsplit(".", 1)[0]
        if url_basename.lower() in _GENERIC_BASENAMES:
            url_basename = source_id.replace("-", "_")
        basename = url_basename

    filename = f"{time_part}_{basename}.{ext}"
    return f"{source_id}/raw/{date_path}/{filename}"


def land_raw(
    source_id: str,
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    ext: str = "bin",
    timeout_s: int = 60,
    notes: str | None = None,
    basename: str | None = None,
) -> LandingResult:
    """Fetch a URL and land its raw body in Azure Blob Storage.

    Returns a LandingResult suitable for JSONL logging. Never raises — errors
    are captured in the result so the per-source test script can continue.
    """
    now = datetime.now(timezone.utc)
    tested_at = now.isoformat()
    container = os.environ.get("AZURE_CONTAINER", "polaris-bronze")

    # Polaris identifies itself on every outbound request. Good citizen + useful
    # for source operators correlating traffic.
    request_headers = {
        "User-Agent": (
            "Polaris/0.1 (Canadian public-data intelligence; "
            "contact: muhammadut@gmail.com)"
        ),
    }
    if headers:
        request_headers.update(headers)

    try:
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            resp = client.request(method, url, headers=request_headers, params=params)
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        return LandingResult(
            source_id=source_id,
            url=url,
            ok=False,
            tested_at=tested_at,
            http_status=e.response.status_code,
            error=str(e),
            error_type=type(e).__name__,
            blocker_type="http_error",
            notes=notes,
        )
    except httpx.RequestError as e:
        return LandingResult(
            source_id=source_id,
            url=url,
            ok=False,
            tested_at=tested_at,
            error=str(e),
            error_type=type(e).__name__,
            blocker_type="network_error",
            notes=notes,
        )

    blob_path = _build_blob_path(source_id, url, ext, now, basename=basename)

    try:
        client = _blob_service_client()
        blob_client = client.get_blob_client(container=container, blob=blob_path)
        blob_client.upload_blob(resp.content, overwrite=True)
    except Exception as e:
        return LandingResult(
            source_id=source_id,
            url=url,
            ok=False,
            tested_at=tested_at,
            http_status=resp.status_code,
            bytes=len(resp.content),
            error=str(e),
            error_type=type(e).__name__,
            blocker_type="storage_error",
            notes=notes,
        )

    return LandingResult(
        source_id=source_id,
        url=url,
        ok=True,
        tested_at=tested_at,
        http_status=resp.status_code,
        content_type=resp.headers.get("content-type"),
        bytes=len(resp.content),
        blob_path=blob_path,
        notes=notes,
    )


def append_result(result: LandingResult, path: str | Path = "phase1-results.jsonl") -> None:
    """Append one result as JSONL to the phase-1 log."""
    path = Path(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result.to_dict()) + "\n")
