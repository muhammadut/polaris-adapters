"""BOIE CSVs + BOIE PDFs + PBO publication detail pages + PBO PDFs.

- BOIE: 10 HOER CSVs (House Officer Expenditure Reports) directly linked
- BOIE: 116 PDF links from the reports index page
- PBO: 15 publication detail pages + any PDFs linked therein
"""
from __future__ import annotations
import time, re
from datetime import datetime, timezone
import httpx
from bs4 import BeautifulSoup
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def land_file(client, blob_service, url, source_id, ext, basename_hint, note):
    now = datetime.now(timezone.utc)
    try:
        r = client.get(url)
        r.raise_for_status()
    except Exception as e:
        append_result(LandingResult(
            source_id=source_id, url=url, ok=False,
            tested_at=now.isoformat(), error=str(e),
            error_type=type(e).__name__, blocker_type="http_error",
            notes=note,
        ))
        return False, 0
    # sanitize basename
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', basename_hint)[:80]
    blob_path = f"{source_id}/raw/{now.strftime('%Y-%m-%d')}/{safe}.{ext}"
    try:
        blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
    except Exception as e:
        append_result(LandingResult(
            source_id=source_id, url=url, ok=False,
            tested_at=now.isoformat(), bytes=len(r.content),
            error=str(e), error_type=type(e).__name__, blocker_type="storage_error",
            notes=note,
        ))
        return False, 0
    append_result(LandingResult(
        source_id=source_id, url=url, ok=True, tested_at=now.isoformat(),
        http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
        notes=note,
    ))
    return True, len(r.content)


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok = fail = 0
    total_bytes = 0

    with httpx.Client(timeout=120, follow_redirects=True, headers=headers) as client:
        # 1. BOIE CSVs + PDFs from the index we already landed
        boie_raw = blob_service.get_blob_client(
            container="polaris-bronze",
            blob="boie-mp-expenses/raw/2026-04-21/06-51-51_reports_index.html",
        ).download_blob().readall()
        soup = BeautifulSoup(boie_raw, "lxml")

        print("\n=== BOIE CSVs ===", flush=True)
        csv_links = [a["href"] for a in soup.find_all("a", href=True) if ".csv" in a.get("href", "").lower()]
        for href in csv_links:
            full = href if href.startswith("http") else f"https://www.ourcommons.ca{href}"
            basename = href.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            s, n = land_file(client, blob_service, full, "boie-mp-expenses", "csv", basename, "BOIE CSV")
            if s: ok += 1; total_bytes += n
            else: fail += 1
            print(f"  [BOIE] {'OK' if s else 'FAIL'} {basename}  ({n:,} B)", flush=True)
            time.sleep(0.3)

        print(f"\n=== BOIE PDFs ({sum(1 for a in soup.find_all('a', href=True) if '.pdf' in a.get('href','').lower())}) ===", flush=True)
        pdf_links = list({a["href"] for a in soup.find_all("a", href=True) if ".pdf" in a.get("href", "").lower()})
        for i, href in enumerate(pdf_links):
            full = href if href.startswith("http") else f"https://www.ourcommons.ca{href}"
            basename = href.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            s, n = land_file(client, blob_service, full, "boie-mp-expenses", "pdf", basename, "BOIE PDF")
            if s: ok += 1; total_bytes += n
            else: fail += 1
            if i % 20 == 0 or not s:
                print(f"  [BOIE PDF {i+1}/{len(pdf_links)}] {'OK' if s else 'FAIL'}  {basename[:60]}", flush=True)
            time.sleep(0.2)

        # 2. PBO — fetch each publication detail page + any PDFs found
        print(f"\n=== PBO publication detail pages ===", flush=True)
        pbo_raw = blob_service.get_blob_client(
            container="polaris-bronze",
            blob="pbo-reports-rendered/raw/2026-04-21/14-30-31_publications_rendered.html",
        ).download_blob().readall()
        pbo_soup = BeautifulSoup(pbo_raw, "lxml")
        pub_pages = list({a["href"] for a in pbo_soup.find_all("a", href=True) if "/publications/" in a.get("href", "")})

        all_pdfs = set()
        for href in pub_pages:
            full = href if href.startswith("http") else f"https://www.pbo-dpb.ca{href}"
            basename = href.rsplit("/", 1)[-1][:60]
            s, n = land_file(client, blob_service, full, "pbo-reports", "html", basename, "PBO detail page")
            if s:
                ok += 1; total_bytes += n
                # parse this page for PDFs
                try:
                    detail_raw = blob_service.get_blob_client(
                        container="polaris-bronze",
                        blob=f"pbo-reports/raw/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/{re.sub(chr(0x5b)+'^A-Za-z0-9_.-'+chr(0x5d),'_', basename)[:80]}.html",
                    ).download_blob().readall()
                    detail_soup = BeautifulSoup(detail_raw, "lxml")
                    for a in detail_soup.find_all("a", href=True):
                        h = a["href"]
                        if ".pdf" in h.lower():
                            full_pdf = h if h.startswith("http") else f"https://www.pbo-dpb.ca{h}"
                            all_pdfs.add(full_pdf)
                except Exception:
                    pass
            else:
                fail += 1
            print(f"  [PBO page] {'OK' if s else 'FAIL'} {basename[:60]}", flush=True)
            time.sleep(0.3)

        print(f"\n=== PBO PDFs ({len(all_pdfs)} discovered) ===", flush=True)
        for i, url in enumerate(sorted(all_pdfs)):
            basename = url.rsplit("/", 1)[-1].rsplit(".", 1)[0][:60]
            s, n = land_file(client, blob_service, url, "pbo-reports", "pdf", basename, "PBO report PDF")
            if s: ok += 1; total_bytes += n
            else: fail += 1
            print(f"  [PBO PDF {i+1}] {'OK' if s else 'FAIL'}  {basename[:50]}  ({n:,} B)", flush=True)
            time.sleep(0.3)

    print(f"\n=== boie_pbo_bulk summary: {ok} OK, {fail} fail, {total_bytes/1024/1024:.1f} MB ===", flush=True)


if __name__ == "__main__":
    main()
