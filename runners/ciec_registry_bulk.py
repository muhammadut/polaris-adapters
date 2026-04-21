"""CIEC Public Registry — fetch all navigation pages + Gifts SharePoint list.

The CIEC site has these registry categories:
  - Gifts                (/EN/PublicRegistries/Pages/Gifts.aspx)
  - PublicRegistry       (MP disclosures under the Conflict of Interest Code)
  - PublicRegistryAct    (Public Office Holders under the Act)
  - PublicRegistryCode   (MPs under the Code)
  - SponsoredTravel

Plus the SharePoint Lists/Gifts/AllItems.aspx backs the Gifts category.
This runner grabs all category landing pages + the main Gifts list + attempts
to enumerate per-MP disclosures.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


CATEGORY_PAGES = [
    "https://prciec-rpccie.parl.gc.ca/EN/PublicRegistries/Pages/Gifts.aspx",
    "https://prciec-rpccie.parl.gc.ca/EN/PublicRegistries/Pages/PublicRegistry.aspx",
    "https://prciec-rpccie.parl.gc.ca/EN/PublicRegistries/Pages/PublicRegistryAct.aspx",
    "https://prciec-rpccie.parl.gc.ca/EN/PublicRegistries/Pages/PublicRegistryCode.aspx",
    "https://prciec-rpccie.parl.gc.ca/EN/PublicRegistries/Pages/SponsoredTravel.aspx",
    # Plus the SharePoint Lists
    "https://prciec-rpccie.parl.gc.ca/Lists/Gifts/AllItems.aspx",
]


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok = 0
    all_detail_urls = set()

    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        # First pass: land each category page
        for url in CATEGORY_PAGES:
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception as e:
                print(f"  FAIL {url}: {e}", flush=True)
                continue
            slug = re.sub(r"[^A-Za-z0-9_.-]", "_", url.rsplit("/", 1)[-1].split("?")[0][:80])
            blob_path = f"ciec-registry/raw/2026-04-21/categories/{slug}"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="ciec-registry", url=url, ok=True,
                tested_at=now.isoformat(), http_status=r.status_code,
                bytes=len(r.content), blob_path=blob_path,
                notes=f"CIEC category page",
            ))
            ok += 1
            print(f"  OK {len(r.content):>8,} B  {slug}", flush=True)

            # Harvest detail/MP-level URLs
            for m in re.finditer(r'href="([^"]+(?:DisplayForm|Details|RegEntry|PublicRegistry[^"]*Details)[^"]*)"', r.text):
                link = m.group(1)
                full = link if link.startswith("http") else f"https://prciec-rpccie.parl.gc.ca{link}"
                all_detail_urls.add(full)
            # Also SharePoint list items pattern
            for m in re.finditer(r'href="(/Lists/Gifts/[^"]+\.aspx[^"]*)"', r.text):
                full = f"https://prciec-rpccie.parl.gc.ca{m.group(1)}"
                all_detail_urls.add(full)
            time.sleep(0.4)

    print(f"\nCategory pages: {ok} OK. Discovered {len(all_detail_urls)} detail URLs.", flush=True)

    # Land a sample of detail URLs (cap at 300 to keep session manageable)
    detail_ok = detail_fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for i, url in enumerate(sorted(all_detail_urls)[:300]):
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception:
                detail_fail += 1; continue
            slug = re.sub(r"[^A-Za-z0-9_.-]", "_", url.rsplit("/", 1)[-1].split("?")[0][:80])
            if not slug: slug = f"detail_{i}"
            blob_path = f"ciec-registry/raw/2026-04-21/details/{i:04d}_{slug}"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="ciec-registry", url=url, ok=True,
                tested_at=now.isoformat(), http_status=r.status_code,
                bytes=len(r.content), blob_path=blob_path,
                notes="CIEC detail",
            ))
            detail_ok += 1
            if detail_ok % 25 == 0:
                print(f"  details: {detail_ok}", flush=True)
            time.sleep(0.3)
    print(f"\n=== CIEC: {ok} categories, {detail_ok} details OK; {detail_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
