"""Patch: fetch sitting days 221-500 for sessions that hit the previous 220 cap.

Affected sessions: 411 (41-1), 412 (41-2), 421 (42-1), 441 (44-1).
42-1 goes to ~day 420+. 44-1 to ~350+.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

SESSIONS = ["411", "412", "421", "441"]
START = 221
END = 500


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for sess in SESSIONS:
            consecutive_404 = 0
            sess_ok = 0
            for day in range(START, END + 1):
                day_str = f"{day:03d}"
                url = f"https://www.ourcommons.ca/Content/House/{sess}/Debates/{day_str}/HAN{day_str}-E.XML"
                now = datetime.now(timezone.utc)
                try:
                    r = client.get(url)
                except Exception:
                    consecutive_404 += 1
                    if consecutive_404 >= 5: break
                    continue
                if r.status_code != 200 or len(r.content) < 2000:
                    consecutive_404 += 1
                    if consecutive_404 >= 5:
                        print(f"  [{sess}] stop at day {day_str} after 5 misses", flush=True)
                        break
                    continue
                consecutive_404 = 0
                blob_path = f"federal-hansard-house-historical/raw/{now.strftime('%Y-%m-%d')}/HAN{sess}_day{day_str}.xml"
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                append_result(LandingResult(
                    source_id="federal-hansard-house-historical",
                    url=url, ok=True, tested_at=now.isoformat(),
                    http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                    notes=f"cap-patch Hansard {sess} day {day_str}",
                ))
                ok += 1; sess_ok += 1
                if sess_ok % 25 == 0:
                    print(f"  [{sess}] patched through day {day_str} ({sess_ok} landed)", flush=True)
                time.sleep(0.25)
            print(f"  [{sess}] DONE — {sess_ok} extra days patched", flush=True)
    print(f"\n=== Hansard cap-patch: {ok} additional days landed ===", flush=True)


if __name__ == "__main__":
    main()
