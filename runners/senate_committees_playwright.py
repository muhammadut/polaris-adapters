"""Senate committees via Playwright — walk landing + transcripts page for each
Senate committee × session to collect individual meeting URLs, then fetch each.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

# Common Senate committee acronyms (ISG+GRO era + legacy)
# These vary by parliament; not all exist in every session.
COMMITTEES = [
    "AEFA",  # Foreign Affairs and International Trade
    "AGFO",  # Agriculture and Forestry
    "ANTR",  # Anti-terrorism
    "APPA",  # Aboriginal Peoples
    "ARCT",  # Arctic
    "AUDI",  # Audit and Oversight
    "BANC",  # Banking, Commerce and the Economy
    "CIBA",  # Internal Economy, Budgets and Administration
    "CSSB",  # Conflict of Interest for Senators
    "ENEV",  # Energy, the Environment and Natural Resources
    "ETHI",  # Ethics and Conflict of Interest
    "FINA",  # National Finance
    "FISH",  # Fisheries and Oceans
    "HUMA",  # Human Rights
    "LCJC",  # Legal and Constitutional Affairs
    "NFFN",  # National Finance (legacy)
    "OLLO",  # Official Languages
    "POFO",  # Selection
    "RIDR",  # Rules, Procedures, Rights of Parliament
    "SECD",  # National Security and Defence
    "SMSM",  # Social Affairs, Science and Technology
    "SOCI",  # Social Affairs, Science and Technology (older)
    "TRCM",  # Transport and Communications
]

SESSIONS = ["45-1","44-1","43-2","43-1","42-1","41-2","41-1","40-3","40-2","40-1","39-2","39-1","38-1"]


def harvest_transcripts_for(page, acr, sess):
    urls = set()
    for base in [
        f"https://sencanada.ca/en/committees/{acr.lower()}/transcriptsminutes/{sess}",
        f"https://sencanada.ca/en/committees/{acr}/transcriptsminutes/{sess}",
    ]:
        try:
            page.goto(base, wait_until="networkidle", timeout=25000)
        except Exception:
            continue
        time.sleep(2)
        for _ in range(25):
            prev = len(urls)
            hrefs = page.eval_on_selector_all(
                'a[href*="/transcripts"]',
                'els => els.map(e => e.getAttribute("href"))')
            for h in hrefs:
                if h and "transcripts" in h and h.count("/") >= 5:
                    full = h if h.startswith("http") else f"https://sencanada.ca{h}"
                    urls.add(full)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            if len(urls) == prev:
                break
    return urls


def main():
    blob_service = _blob_service_client()
    all_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=BROWSER_UA)
        page = ctx.new_page()
        for sess in SESSIONS:
            for acr in COMMITTEES:
                got = harvest_transcripts_for(page, acr, sess)
                if got:
                    print(f"  [{acr} {sess}] {len(got)} transcript URLs", flush=True)
                    all_urls.update(got)
        browser.close()

    print(f"\nTotal unique Senate committee transcript URLs: {len(all_urls)}", flush=True)

    ok = fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers={"User-Agent": BROWSER_UA}) as client:
        for url in sorted(all_urls):
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                fail += 1; continue
            slug = url.rsplit("/", 1)[-1][:80]
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", slug)
            blob_path = f"senate-committee-transcripts/raw/2026-04-21/{safe}.html"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="senate-committee-transcripts", url=url, ok=True,
                tested_at=now.isoformat(), http_status=r.status_code,
                bytes=len(r.content), blob_path=blob_path,
                notes=f"Senate committee transcript",
            ))
            ok += 1
            if ok % 50 == 0:
                print(f"  fetched {ok}", flush=True)
            time.sleep(0.25)
    print(f"\n=== Senate committees: {ok} OK, {fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
