"""Historical committee backfill — same enumerator as 45-1 but for 44-1.

Structure of runner is identical to house_committees_enumerator.py; only the
parl-session constants change. Phase 2 will unify these into a parameterized
runner + a discovery sweep for all working parliament-sessions.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

COMMITTEES = ["FINA", "HESA", "INDU", "JUST", "PROC", "ETHI", "AGRI", "ENVI", "SECU", "OGGO"]
PARL_SESSION = "44-1"
PARL_SESSION_PATH = "441"


def list_meetings(client, acr):
    try:
        r = client.get(f"https://www.ourcommons.ca/Committees/en/{acr}/Meetings?parl=44&session=1")
        r.raise_for_status()
    except Exception as e:
        print(f"  [!] {acr}: index fetch failed — {e}")
        return []
    nums = set()
    for m in re.finditer(rf"/DocumentViewer/en/{PARL_SESSION}/{acr}/meeting-(\d+)/evidence", r.text):
        nums.add(int(m.group(1)))
    return sorted(nums)


def xml_url_for_meeting(client, acr, n):
    try:
        r = client.get(f"https://www.ourcommons.ca/DocumentViewer/en/{PARL_SESSION}/{acr}/meeting-{n}/evidence")
        r.raise_for_status()
    except Exception:
        return None
    m = re.search(rf"(/Content/Committee/{PARL_SESSION_PATH}/{acr}/Evidence/EV\d+/{acr}EV\d+-E\.XML)", r.text, re.I)
    return "https://www.ourcommons.ca" + m.group(1) if m else None


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok = fail = no_xml = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for acr in COMMITTEES:
            print(f"\n=== {acr} ({PARL_SESSION}) ===")
            meetings = list_meetings(client, acr)
            if not meetings:
                print(f"  no meetings found")
                continue
            print(f"  meetings: {len(meetings)} (first 5: {meetings[:5]})")
            for n in meetings:
                time.sleep(0.4)
                xml_url = xml_url_for_meeting(client, acr, n)
                if not xml_url:
                    no_xml += 1
                    continue
                now = datetime.now(timezone.utc)
                try:
                    r = client.get(xml_url)
                    r.raise_for_status()
                except Exception as e:
                    print(f"    meeting-{n:02d}  FAIL {type(e).__name__}")
                    fail += 1
                    continue
                blob_path = f"house-committee-transcripts/raw/{now.strftime('%Y-%m-%d')}/{acr}_{PARL_SESSION}_meeting-{n:02d}.xml"
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
                append_result(LandingResult(
                    source_id="house-committee-transcripts",
                    url=xml_url, ok=True, tested_at=now.isoformat(),
                    http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                    notes=f"{acr} {PARL_SESSION} meeting-{n}",
                ))
                print(f"    meeting-{n:02d}  OK  {len(r.content):>8,} B")
                ok += 1
    print(f"\n=== Summary 44-1: {ok} OK, {fail} fail, {no_xml} no-XML ===")


if __name__ == "__main__":
    main()
