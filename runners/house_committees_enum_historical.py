"""Historical committee backfill — 43-1 and 42-1 for the same 10 major committees."""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

COMMITTEES = ["FINA", "HESA", "INDU", "JUST", "PROC", "ETHI", "AGRI", "ENVI", "SECU", "OGGO"]

# (parliament-session-url-param, parliament-session-path-form, display)
SESSIONS = [
    ("43", "1", "43-1", "431"),  # Oct 2019 - Oct 2021
    ("42", "1", "42-1", "421"),  # Oct 2015 - Oct 2019
]


def list_meetings(client, acr, parl, sess, display):
    try:
        r = client.get(f"https://www.ourcommons.ca/Committees/en/{acr}/Meetings?parl={parl}&session={sess}")
        r.raise_for_status()
    except Exception as e:
        print(f"  [!] {acr} {display}: index fail — {e}")
        return []
    nums = set()
    for m in re.finditer(rf"/DocumentViewer/en/{display}/{acr}/meeting-(\d+)/evidence", r.text):
        nums.add(int(m.group(1)))
    return sorted(nums)


def xml_url(client, acr, n, display, path_form):
    try:
        r = client.get(f"https://www.ourcommons.ca/DocumentViewer/en/{display}/{acr}/meeting-{n}/evidence")
        r.raise_for_status()
    except Exception:
        return None
    m = re.search(rf"(/Content/Committee/{path_form}/{acr}/Evidence/EV\d+/{acr}EV\d+-E\.XML)", r.text, re.I)
    return "https://www.ourcommons.ca" + m.group(1) if m else None


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    grand_ok = grand_fail = 0

    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for parl, sess, display, path_form in SESSIONS:
            print(f"\n=============== {display} ===============", flush=True)
            for acr in COMMITTEES:
                meetings = list_meetings(client, acr, parl, sess, display)
                if not meetings:
                    print(f"  [{acr} {display}] no meetings found", flush=True)
                    continue
                print(f"  [{acr} {display}] {len(meetings)} meetings — starting", flush=True)
                for n in meetings:
                    time.sleep(0.4)
                    url = xml_url(client, acr, n, display, path_form)
                    if not url: continue
                    now = datetime.now(timezone.utc)
                    try:
                        r = client.get(url); r.raise_for_status()
                    except Exception as e:
                        grand_fail += 1
                        continue
                    blob_path = f"house-committee-transcripts/raw/2026-04-21/{acr}_{display}_meeting-{n:02d}.xml"
                    blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                    append_result(LandingResult(
                        source_id="house-committee-transcripts",
                        url=url, ok=True, tested_at=now.isoformat(),
                        http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                        notes=f"{acr} {display} meeting-{n}",
                    ))
                    grand_ok += 1
                    if grand_ok % 50 == 0:
                        print(f"    running total OK: {grand_ok}", flush=True)
    print(f"\n=== Historical committees (43-1 + 42-1): {grand_ok} OK, {grand_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
