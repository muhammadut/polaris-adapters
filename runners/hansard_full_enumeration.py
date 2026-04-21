"""Full historical Hansard enumeration — every sitting day per parliament-session.

Enumerates sitting-day numbers by probing meeting-1, meeting-2, ... until
consecutive 404s. For each working parliament-session, lands every sitting
day's Evidence XML.

Scope: 38-1 (2004) through 45-1 (2025) — 9 parliament-sessions.
Estimated: ~1500-2000 XMLs, ~200-300 MB total.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


PARL_SESSIONS = ["381", "391", "392", "401", "402", "403", "411", "412", "421", "431", "441", "451"]

MAX_DAY_PER_SESSION = 220  # defensive upper bound; session with most sitting days historically
CONSECUTIVE_404_STOP = 5   # stop scanning a session after 5 consecutive misses


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    total_ok = total_fail = 0

    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for sess in PARL_SESSIONS:
            print(f"\n=== Parliament-session {sess} ===", flush=True)
            sess_ok = 0
            consecutive_404 = 0
            for day in range(1, MAX_DAY_PER_SESSION + 1):
                day_str = f"{day:03d}"
                url = f"https://www.ourcommons.ca/Content/House/{sess}/Debates/{day_str}/HAN{day_str}-E.XML"
                now = datetime.now(timezone.utc)
                try:
                    r = client.get(url)
                except Exception as e:
                    print(f"  [{sess}] day {day:03d}: ERR {type(e).__name__}", flush=True)
                    consecutive_404 += 1
                    if consecutive_404 >= CONSECUTIVE_404_STOP:
                        print(f"  [{sess}] stopping after {CONSECUTIVE_404_STOP} consecutive misses", flush=True)
                        break
                    time.sleep(0.5)
                    continue

                if r.status_code == 404 or (r.status_code == 200 and len(r.content) < 2000):
                    consecutive_404 += 1
                    if consecutive_404 >= CONSECUTIVE_404_STOP:
                        print(f"  [{sess}] stopping after {CONSECUTIVE_404_STOP} consecutive misses at day {day:03d}", flush=True)
                        break
                    time.sleep(0.3)
                    continue

                if r.status_code != 200:
                    total_fail += 1
                    consecutive_404 = 0
                    time.sleep(0.3)
                    continue

                consecutive_404 = 0
                blob_path = f"federal-hansard-house-historical/raw/{now.strftime('%Y-%m-%d')}/HAN{sess}_day{day_str}.xml"
                try:
                    blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                except Exception as e:
                    print(f"  [{sess}] day {day:03d} storage FAIL: {e}", flush=True)
                    total_fail += 1
                    continue

                append_result(LandingResult(
                    source_id="federal-hansard-house-historical",
                    url=url, ok=True, tested_at=now.isoformat(),
                    http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                    notes=f"Hansard {sess} day {day_str}",
                ))
                sess_ok += 1
                total_ok += 1
                if sess_ok % 25 == 0:
                    print(f"  [{sess}] day {day:03d} — {len(r.content):,} B  (session running total: {sess_ok})", flush=True)
                time.sleep(0.25)

            print(f"  [{sess}] DONE — {sess_ok} sitting days landed", flush=True)

    print(f"\n=== Full historical Hansard: {total_ok} OK, {total_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
