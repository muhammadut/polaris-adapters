"""Deep historical committee backfill — 38-1 through 41-2.

Runs all 29 committees across 8 additional parliament-sessions that chamber
Hansard proved the URL pattern works for. If any committee didn't exist in
an older session (e.g., AMAD formed later), list_meetings returns empty —
we just skip.

Estimated: potentially 5,000-10,000 more XMLs depending on how many
committees existed and how active they were.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

ALL_COMMITTEES = [
    "ACVA","AGRI","AMAD","BCAN","BILI","CHPC","CIIT","CIMM","ENVI","ETHI",
    "FAAE","FEWO","FINA","FOPO","HESA","HUMA","INAN","INDU","JUST","LANG",
    "LIAI","NDDN","OGGO","PACP","PROC","REGS","RNNR","SECU","TRAN",
]

HISTORICAL_SESSIONS = [
    ("41","2","41-2","412"),
    ("41","1","41-1","411"),
    ("40","3","40-3","403"),
    ("40","2","40-2","402"),
    ("40","1","40-1","401"),
    ("39","2","39-2","392"),
    ("39","1","39-1","391"),
    ("38","1","38-1","381"),
]


def list_meetings(client, acr, parl, sess, display):
    try:
        r = client.get(f"https://www.ourcommons.ca/Committees/en/{acr}/Meetings?parl={parl}&session={sess}")
        r.raise_for_status()
    except Exception:
        return []
    return sorted({int(m.group(1)) for m in re.finditer(
        rf"/DocumentViewer/en/{display}/{acr}/meeting-(\d+)/evidence", r.text)})


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
        for parl, sess, display, path_form in HISTORICAL_SESSIONS:
            print(f"\n=============== {display} ===============", flush=True)
            session_ok = 0
            for acr in ALL_COMMITTEES:
                meetings = list_meetings(client, acr, parl, sess, display)
                if not meetings:
                    continue
                print(f"  [{acr} {display}] {len(meetings)} meetings", flush=True)
                for n in meetings:
                    time.sleep(0.35)
                    url = xml_url(client, acr, n, display, path_form)
                    if not url:
                        continue
                    now = datetime.now(timezone.utc)
                    try:
                        r = client.get(url); r.raise_for_status()
                    except Exception:
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
                    session_ok += 1
            print(f"  ** {display} session total: {session_ok} **", flush=True)
    print(f"\n=== Deep historical committees (38-1 → 41-2): {grand_ok} OK, {grand_fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
