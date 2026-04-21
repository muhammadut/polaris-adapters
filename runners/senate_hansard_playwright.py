"""Senate chamber debates via Playwright.

Visits each session's archive page, scrolls to load more, extracts every
debate URL, then fetches each one's HTML.

Senate sessions tried: 45-1 through 38-1 (same era OurCommons House covers).
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


# (parl-sess display, URL suffix)
SESSIONS = ["45-1","44-1","43-2","43-1","42-1","41-2","41-1","40-3","40-2","40-1",
            "39-2","39-1","38-1"]


def harvest_debate_urls_for_session(page, sess):
    urls = set()
    for base in [f"https://sencanada.ca/en/in-the-chamber/debates/{sess}"]:
        try:
            page.goto(base, wait_until="networkidle", timeout=30000)
        except Exception:
            continue
        time.sleep(2)
        # Scroll to bottom repeatedly to trigger lazy loading
        for _ in range(30):
            prev_count = len(urls)
            hrefs = page.eval_on_selector_all(
                'a[href*="/en/content/sen/chamber/"][href*="/debates/"]',
                'els => els.map(e => e.getAttribute("href"))')
            for h in hrefs:
                if h and "/debates/" in h and h.count("/") >= 6:
                    full = h if h.startswith("http") else f"https://sencanada.ca{h}"
                    urls.add(full)
            # scroll
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.2)
            # look for pagination controls
            for sel in ['button[aria-label*="Next" i]', 'a[aria-label*="Next" i]',
                        'a.pagination-next', 'button.load-more', 'a:has-text("Next")']:
                try:
                    el = page.query_selector(sel)
                    if el and el.is_visible() and el.is_enabled():
                        el.click()
                        page.wait_for_load_state("networkidle", timeout=8000)
                        time.sleep(1)
                        break
                except Exception:
                    pass
            if len(urls) == prev_count:
                # stable for one iteration — good indicator we're at the end
                pass
    return urls


def main():
    blob_service = _blob_service_client()
    all_urls = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=BROWSER_UA)
        page = ctx.new_page()
        for sess in SESSIONS:
            print(f"\n=== Senate {sess} ===", flush=True)
            found = harvest_debate_urls_for_session(page, sess)
            all_urls[sess] = sorted(found)
            print(f"  {sess}: {len(found)} debate URLs discovered", flush=True)
        browser.close()

    # Now fetch each debate's HTML
    ok = fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers={"User-Agent": BROWSER_UA}) as client:
        for sess, urls in all_urls.items():
            for url in urls:
                now = datetime.now(timezone.utc)
                try:
                    r = client.get(url); r.raise_for_status()
                except Exception:
                    fail += 1; continue
                slug = url.rsplit("/", 1)[-1][:80]
                safe = re.sub(r"[^A-Za-z0-9_.-]", "_", slug)
                blob_path = f"senate-hansard/raw/2026-04-21/{sess}_{safe}.html"
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                append_result(LandingResult(
                    source_id="senate-hansard", url=url, ok=True,
                    tested_at=now.isoformat(), http_status=r.status_code,
                    bytes=len(r.content), blob_path=blob_path,
                    notes=f"Senate {sess} debate",
                ))
                ok += 1
                time.sleep(0.25)

    print(f"\n=== Senate Hansard total: {ok} debates OK, {fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
