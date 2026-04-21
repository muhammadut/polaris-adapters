"""Remaining 19 main House standing committees × 4 parliaments.

Extends what we already have (10 committees × 45-1, 44-1, 43-1, 42-1) to
cover the rest: ACVA, AMAD, BCAN, BILI, CHPC, CIIT, CIMM, FAAE, FEWO,
FOPO, HUMA, INAN, LANG, LIAI, NDDN, PACP, REGS, RNNR, TRAN.

Estimated: 19 × ~100 meetings avg × 4 parliaments = ~7,000 more XMLs.
Runtime: 30-60 min at polite rate.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result

COMMITTEES = ["ACVA","AMAD","BCAN","BILI","CHPC","CIIT","CIMM","FAAE","FEWO",
              "FOPO","HUMA","INAN","LANG","LIAI","NDDN","PACP","REGS","RNNR","TRAN"]
SESSIONS = [
    ("45","1","45-1","451"),
    ("44","1","44-1","441"),
    ("43","1","43-1","431"),
    ("42","1","42-1","421"),
]


def list_meetings(client, acr, parl, sess, display):
    try:
        r = client.get(f"https://www.ourcommons.ca/Committees/en/{acr}/Meetings?parl={parl}&session={sess}")
        r.raise_for_status()
    except Exception:
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
    grand_ok = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for parl, sess, display, path_form in SESSIONS:
            for acr in COMMITTEES:
                meetings = list_meetings(client, acr, parl, sess, display)
                if not meetings:
                    continue
                print(f"  [{acr} {display}] {len(meetings)} meetings", flush=True)
                for n in meetings:
                    time.sleep(0.35)
                    url = xml_url(client, acr, n, display, path_form)
                    if not url: continue
                    now = datetime.now(timezone.utc)
                    try:
                        r = client.get(url); r.raise_for_status()
                    except Exception:
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
                    if grand_ok % 100 == 0:
                        print(f"    running total OK: {grand_ok}", flush=True)
    print(f"\n=== Remaining committees: {grand_ok} OK ===", flush=True)


if __name__ == "__main__":
    main()
