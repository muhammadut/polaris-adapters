"""Auditor General reports — fetch index + all 149 report pages + PDFs.

Uses the canada.ca reports index discovered from user's manual navigation.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}

    # 1. Fetch the index
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        r = client.get("https://www.canada.ca/en/auditor-general/our-work/audit-reports.html")
        r.raise_for_status()
    index_html = r.content

    # Save the index
    now = datetime.now(timezone.utc)
    blob_path = f"auditor-general-reports/raw/2026-04-21/audit_reports_index.html"
    blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(index_html, overwrite=True)
    print(f"Index landed: {len(index_html):,} B", flush=True)

    # 2. Extract all report URLs
    report_paths = sorted(set(re.findall(
        r'href="(/en/auditor-general/[^"]+\.html)"',
        index_html.decode("utf-8", errors="replace"))))
    print(f"Found {len(report_paths)} report URLs", flush=True)

    # 3. Fetch each report + extract PDFs
    ok = fail = pdf_ok = pdf_fail = 0
    all_pdfs = set()
    with httpx.Client(timeout=120, follow_redirects=True, headers=headers) as client:
        for path in report_paths:
            url = "https://www.canada.ca" + path
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                fail += 1; continue
            slug = re.sub(r"[^A-Za-z0-9_.-]", "_", path.rsplit("/", 1)[-1][:80])
            blob_path = f"auditor-general-reports/raw/2026-04-21/reports/{slug}"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="auditor-general-reports", url=url, ok=True,
                tested_at=now.isoformat(), http_status=r.status_code,
                bytes=len(r.content), blob_path=blob_path, notes="AG report page",
            ))
            ok += 1

            # Extract PDF links
            for m in re.finditer(r'href="([^"]+\.pdf)"', r.text):
                link = m.group(1)
                full = link if link.startswith("http") else (
                    f"https://www.canada.ca{link}" if link.startswith("/") else None
                )
                if full and ("auditor-general" in full.lower() or "oag" in full.lower() or "bvg" in full.lower()):
                    all_pdfs.add(full)
            time.sleep(0.25)

    print(f"\n{ok} report pages landed. {len(all_pdfs)} PDF URLs discovered.", flush=True)

    # 4. Fetch PDFs
    with httpx.Client(timeout=180, follow_redirects=True, headers=headers) as client:
        for url in sorted(all_pdfs):
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                pdf_fail += 1; continue
            slug = re.sub(r"[^A-Za-z0-9_.-]", "_", url.rsplit("/", 1)[-1].split("?")[0][:80])
            if not slug.lower().endswith(".pdf"): slug += ".pdf"
            blob_path = f"auditor-general-reports/raw/2026-04-21/pdfs/{slug}"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="auditor-general-reports", url=url, ok=True,
                tested_at=now.isoformat(), http_status=r.status_code,
                bytes=len(r.content), blob_path=blob_path, notes="AG report PDF",
            ))
            pdf_ok += 1
            if pdf_ok % 20 == 0:
                print(f"  PDFs: {pdf_ok}/{len(all_pdfs)}", flush=True)
            time.sleep(0.3)

    print(f"\n=== AG reports: {ok} pages, {pdf_ok} PDFs OK; {fail}+{pdf_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
