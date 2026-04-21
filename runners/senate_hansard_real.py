"""Senate Hansard done right — direct HTML scrape of archive pages.

Each /en/in-the-chamber/debates/<parl>-<sess> page has every debate
identifier (NNNdb_YYYY-MM-DD-e) embedded in HTML. We scrape all of them,
construct debate URLs, fetch each one.

Senate archives go back to 35-1 (mid-1990s) — deeper than House XML (38-1).
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

SESSIONS = ["45-1","44-1","43-2","43-1","42-1","41-2","41-1","40-3","40-2","40-1",
            "39-2","39-1","38-1","37-3","37-2","37-1","36-2","36-1","35-2","35-1"]


def harvest_identifiers(client, sess):
    """Returns list of debate identifiers like '069db_2022-10-17-e'."""
    try:
        r = client.get(f"https://sencanada.ca/en/in-the-chamber/debates/{sess}")
        r.raise_for_status()
    except Exception:
        return []
    return sorted(set(re.findall(r"(\d{1,3}db_\d{4}-\d{2}-\d{2}-e)", r.text)))


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    grand_ok = grand_fail = 0

    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for sess in SESSIONS:
            # sess looks like "44-1"; URL path form is the same
            path_form = sess.replace("-", "")  # 441
            ids = harvest_identifiers(client, sess)
            if not ids:
                print(f"  [{sess}] no identifiers found (session may not exist)", flush=True)
                continue
            print(f"\n  [{sess}] {len(ids)} debates — fetching", flush=True)
            sess_ok = 0
            for ident in ids:
                url = f"https://sencanada.ca/en/content/sen/chamber/{path_form}/debates/{ident}"
                now = datetime.now(timezone.utc)
                try:
                    r = client.get(url); r.raise_for_status()
                except Exception:
                    grand_fail += 1
                    continue
                blob_path = f"senate-hansard/raw/2026-04-21/{sess}_{ident}.html"
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                append_result(LandingResult(
                    source_id="senate-hansard", url=url, ok=True,
                    tested_at=now.isoformat(), http_status=r.status_code,
                    bytes=len(r.content), blob_path=blob_path,
                    notes=f"Senate {sess} {ident}",
                ))
                grand_ok += 1
                sess_ok += 1
                if sess_ok % 50 == 0:
                    print(f"    [{sess}] {sess_ok}/{len(ids)}", flush=True)
                time.sleep(0.25)
            print(f"  [{sess}] DONE: {sess_ok}/{len(ids)}", flush=True)
    print(f"\n=== Senate Hansard: {grand_ok} debates OK, {grand_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
