"""Fetch all 236 individual OIC (Information Commissioner) final-report pages."""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}

    index_html = blob_service.get_blob_client(
        container="polaris-bronze",
        blob="oic-decisions/raw/2026-04-21/06-51-48_final_reports_index.html",
    ).download_blob().readall().decode("utf-8", errors="replace")
    report_paths = sorted(set(re.findall(r'href="(/en/decisions/final-reports/[^"]+)"', index_html)))
    print(f"Fetching {len(report_paths)} OIC individual final reports ...", flush=True)

    ok = fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for path in report_paths:
            url = "https://www.oic-ci.gc.ca" + path
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                fail += 1
                continue
            slug = path.rsplit("/", 1)[-1][:80]
            blob_path = f"oic-decisions/raw/2026-04-21/reports/{slug}.html"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="oic-decisions",
                url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                notes=f"OIC final report {slug}",
            ))
            ok += 1
            if ok % 50 == 0:
                print(f"  progress: {ok} / {len(report_paths)}", flush=True)
            time.sleep(0.25)

    print(f"\n=== OIC final reports: {ok} OK, {fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
