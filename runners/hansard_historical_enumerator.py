"""Phase 1 completion: Land 1 sample Hansard XML per parliament-session back to 38-1.

Proves the URL pattern works across 8 parliament-sessions (2004 → 2021) and
seeds the bronze layer with representative historical debates.

Phase 2 extends to ENUMERATE all sitting days per parliament (the earliest
sessions have ~100-200 sitting days each).
"""
from __future__ import annotations
import time, httpx
from datetime import datetime, timezone
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

PARL_SESSIONS = [
    ("381", "2004"),  # 38th Parl, 1st sess — opened 2004-10-04
    ("391", "2006"),  # 39-1
    ("392", "2007"),  # 39-2
    ("401", "2008"),  # 40-1
    ("402", "2009"),  # 40-2
    ("403", "2010"),  # 40-3
    ("411", "2011"),  # 41-1
    ("412", "2013"),  # 41-2
    ("421", "2015"),  # 42-1
]

def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok = 0
    fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for parl_sess, year_hint in PARL_SESSIONS:
            url = f"https://www.ourcommons.ca/Content/House/{parl_sess}/Debates/001/HAN001-E.XML"
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url)
                r.raise_for_status()
            except Exception as e:
                print(f"  [{parl_sess}] FAIL: {e}")
                append_result(LandingResult(
                    source_id="federal-hansard-house-historical",
                    url=url, ok=False, tested_at=now.isoformat(),
                    error=str(e), error_type=type(e).__name__,
                    blocker_type="http_error",
                    notes=f"Hansard {parl_sess} day 001 (~{year_hint})",
                ))
                fail += 1
                time.sleep(0.3)
                continue

            blob_path = f"federal-hansard-house-historical/raw/{now.strftime('%Y-%m-%d')}/HAN{parl_sess}_day001.xml"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)

            print(f"  [{parl_sess}] OK  {len(r.content):>8,} B  (~{year_hint})  -> {blob_path}")
            append_result(LandingResult(
                source_id="federal-hansard-house-historical",
                url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, content_type=r.headers.get("content-type"),
                bytes=len(r.content), blob_path=blob_path,
                notes=f"Hansard {parl_sess} day 001 (~{year_hint}) — historical backfill proof",
            ))
            ok += 1
            time.sleep(0.4)

    print(f"\n=== Historical Hansard: {ok} OK, {fail} fail ===")

if __name__ == "__main__":
    main()
