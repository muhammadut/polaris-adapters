"""OPC (Privacy Commissioner) — enumerate all PIPEDA investigation findings via pagination."""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    all_findings = set()

    # Paginate
    with httpx.Client(timeout=30, follow_redirects=True, headers=headers) as client:
        for page in range(1, 50):
            try:
                r = client.get(
                    f"https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/?Page={page}"
                )
                r.raise_for_status()
            except Exception:
                break
            # PIPEDA findings URLs
            links = re.findall(r'href="(/en/opc-actions-and-decisions/investigations/investigations-into-businesses/\d{4}/pipeda-\d{4}-\d{3,4}/)"', r.text)
            before = len(all_findings)
            all_findings.update(links)
            if len(all_findings) == before and page > 5:
                # no new findings — stop
                print(f"  stopped at page {page} (no new findings)", flush=True)
                break
            time.sleep(0.3)
    print(f"Found {len(all_findings)} unique PIPEDA finding URLs", flush=True)

    # Fetch each
    ok = fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for path in sorted(all_findings):
            url = "https://www.priv.gc.ca" + path
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                fail += 1; continue
            slug = path.strip("/").rsplit("/", 1)[-1][:80]
            blob_path = f"opc-findings/raw/2026-04-21/findings/{slug}.html"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="opc-findings", url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                notes=f"PIPEDA finding {slug}",
            ))
            ok += 1
            time.sleep(0.25)
    print(f"\n=== OPC findings: {ok} OK, {fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
