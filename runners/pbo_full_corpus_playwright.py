"""PBO full corpus via Playwright — paginate the React SPA, extract all
publication-detail URLs, fetch each detail page + any linked PDFs.

The /en/publications page shows 15 items per "page" via client-side paging.
Playwright clicks through pages until done, harvests detail URLs, then fetches.
"""
from __future__ import annotations
import time, re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def harvest_pub_urls():
    urls = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=BROWSER_UA)
        page = ctx.new_page()
        page.goto("https://www.pbo-dpb.ca/en/publications", wait_until="networkidle")
        time.sleep(3)

        # Extract any links with /publications/ in them from the current view
        # and iteratively click "next page" or load-more controls until nothing new
        for _ in range(200):
            hrefs = page.eval_on_selector_all('a[href*="/publications/"]',
                'els => els.map(e => e.getAttribute("href"))')
            before = len(urls)
            for h in hrefs:
                if h and "/publications/" in h and h != "/en/publications":
                    full = h if h.startswith("http") else f"https://www.pbo-dpb.ca{h}"
                    urls.add(full)

            # Try clicking the next-page button (pagination is typical in this SPA)
            clicked = False
            for sel in ['button[aria-label*="Next" i]', 'a[aria-label*="Next" i]',
                        'button[rel="next"]', 'a[rel="next"]',
                        'li.pagination-next a', 'button:has-text("Next")',
                        'a:has-text("Next")', '[class*="pagination"] [class*="next"] a',
                        '[class*="pagination"] [class*="next"] button']:
                try:
                    el = page.query_selector(sel)
                    if el and el.is_visible():
                        el.click()
                        page.wait_for_load_state("networkidle", timeout=8000)
                        time.sleep(1.5)
                        clicked = True
                        break
                except Exception:
                    pass
            if not clicked:
                # Try load-more
                for sel in ['button:has-text("Load more")', 'button:has-text("Show more")',
                            'a:has-text("Load more")']:
                    try:
                        el = page.query_selector(sel)
                        if el and el.is_visible():
                            el.click()
                            page.wait_for_load_state("networkidle", timeout=8000)
                            time.sleep(1.5)
                            clicked = True
                            break
                    except Exception:
                        pass

            if not clicked:
                print(f"  no more pagination after {len(urls)} URLs harvested", flush=True)
                break

            # Stop if no new URLs appeared after clicking
            if len(urls) == before:
                print(f"  pagination still works but no new URLs — stopping at {len(urls)}", flush=True)
                break

        browser.close()
    return sorted(urls)


def main():
    blob_service = _blob_service_client()
    print("Harvesting publication URLs from PBO SPA ...", flush=True)
    pub_urls = harvest_pub_urls()
    print(f"  got {len(pub_urls)} publication URLs", flush=True)

    ok = fail = 0
    all_pdfs = set()
    with httpx.Client(timeout=120, follow_redirects=True, headers={"User-Agent": BROWSER_UA}) as client:
        for url in pub_urls:
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                fail += 1
                continue
            slug = url.rsplit("/", 1)[-1][:80]
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", slug)
            blob_path = f"pbo-reports/raw/2026-04-21/full/{safe}.html"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="pbo-reports", url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                notes=f"PBO publication page {safe}",
            ))
            ok += 1
            # Extract PDF links from this page
            for m in re.finditer(r'href="([^"]+\.pdf[^"]*)"', r.text, re.I):
                link = m.group(1)
                full = link if link.startswith("http") else f"https://www.pbo-dpb.ca{link}"
                all_pdfs.add(full)
            time.sleep(0.25)

    print(f"  landed {ok} publication pages, discovered {len(all_pdfs)} PDF links", flush=True)

    pdf_ok = pdf_fail = 0
    with httpx.Client(timeout=180, follow_redirects=True, headers={"User-Agent": BROWSER_UA}) as client:
        for url in sorted(all_pdfs):
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                pdf_fail += 1
                continue
            slug = url.rsplit("/", 1)[-1].split("?")[0][:80]
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", slug)
            if not safe.endswith(".pdf"): safe += ".pdf"
            blob_path = f"pbo-reports/raw/2026-04-21/pdfs/{safe}"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="pbo-reports", url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                notes=f"PBO PDF {safe}",
            ))
            pdf_ok += 1
            if pdf_ok % 25 == 0:
                print(f"  PDFs: {pdf_ok}/{len(all_pdfs)}", flush=True)
            time.sleep(0.25)

    print(f"\n=== PBO full: {ok} pages, {pdf_ok} PDFs OK; {fail}+{pdf_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
