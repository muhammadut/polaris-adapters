"""Per-MP vote ballots across all sessions — the complete ballot graph.

For each parliament-session where OurCommons returned divisions, enumerate
divisions 1..N and fetch each one's per-MP ballot XML from
  /members/en/votes/<parl>/<sess>/<division>/xml

Each file contains every MP's ballot (yea/nay/paired/absent) for that division.
Phase 2 joins these to ourcommons-mps by PersonId for "how did X vote" queries.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

# (parliament, session, display)
SESSIONS = [
    (45, 1, "45-1"),
    (44, 1, "44-1"),
    (43, 2, "43-2"),
    (43, 1, "43-1"),
    (42, 1, "42-1"),
    (41, 2, "41-2"),
    (41, 1, "41-1"),
    (40, 3, "40-3"),
    (40, 2, "40-2"),
    (40, 1, "40-1"),
    (39, 2, "39-2"),
    (39, 1, "39-1"),
    (38, 1, "38-1"),
]

CONSECUTIVE_404_STOP = 6


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    grand_ok = grand_fail = 0

    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for parl, sess, display in SESSIONS:
            print(f"\n=== {display} ===", flush=True)
            consecutive_404 = 0
            sess_ok = 0
            for div in range(1, 2000):  # defensive upper bound; will stop on 404s
                url = f"https://www.ourcommons.ca/members/en/votes/{parl}/{sess}/{div}/xml"
                now = datetime.now(timezone.utc)
                try:
                    r = client.get(url)
                except Exception:
                    consecutive_404 += 1
                    if consecutive_404 >= CONSECUTIVE_404_STOP: break
                    continue
                if r.status_code != 200 or len(r.content) < 3000:
                    consecutive_404 += 1
                    if consecutive_404 >= CONSECUTIVE_404_STOP:
                        print(f"  [{display}] stop at division {div} after {CONSECUTIVE_404_STOP} misses (last total: {sess_ok})", flush=True)
                        break
                    time.sleep(0.15)
                    continue
                consecutive_404 = 0
                blob_path = f"ourcommons-mp-ballots/raw/2026-04-21/{display}_div-{div:04d}.xml"
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                append_result(LandingResult(
                    source_id="ourcommons-mp-ballots",
                    url=url, ok=True, tested_at=now.isoformat(),
                    http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                    notes=f"{display} division {div} — all-MP ballots",
                ))
                grand_ok += 1
                sess_ok += 1
                if sess_ok % 50 == 0:
                    print(f"  [{display}] {sess_ok} divisions", flush=True)
                time.sleep(0.25)
            print(f"  [{display}] FINAL: {sess_ok} divisions", flush=True)
    print(f"\n=== Per-MP ballots: {grand_ok} divisions, {grand_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
