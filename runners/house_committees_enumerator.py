"""Phase 1 completion: enumerate House committee Evidence XMLs for 45-1.

For each committee in a curated list:
  1. Fetch /Committees/en/<ACR>/Meetings page for the current parl-session
  2. Parse out /DocumentViewer/en/45-1/<ACR>/meeting-<N>/evidence URLs
  3. For each meeting URL, fetch the HTML, extract the direct XML link
  4. Download the XML + upload to Azure under
     `polaris-bronze/house-committee-transcripts/raw/<date>/<ACR>_meeting-<N>.xml`
  5. Log each result to phase1-results.jsonl

Runs for 45-1 (current Parliament). Phase 2 extends to prior parliaments by
changing the `parl-session` constant; same enumerator pattern applies.

This is a bulk job — ~10 committees × ~20 meetings ≈ 200+ XML fetches.
Takes ~10-20 min depending on network. Polite 0.5s delay between requests.

Run: `uv run python -m runners.house_committees_enumerator`
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import httpx

from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


# Curated list of the 10 highest-substance standing committees for 45-1.
# Expand to all ~25 in Phase 2 or when product demands cross-committee queries.
COMMITTEES = [
    "FINA",  # Finance
    "HESA",  # Health
    "INDU",  # Industry & Technology
    "JUST",  # Justice
    "PROC",  # Procedure & House Affairs
    "ETHI",  # Ethics
    "AGRI",  # Agriculture
    "ENVI",  # Environment
    "SECU",  # National Security
    "OGGO",  # Government Operations
]

PARL_SESSION = "45-1"
PARL_SESSION_PATH = "451"  # concatenated form used in /Content/Committee/ URLs


def list_meetings_for_committee(client: httpx.Client, acr: str) -> list[int]:
    """Return sorted list of meeting numbers that have an evidence page."""
    url = f"https://www.ourcommons.ca/Committees/en/{acr}/Meetings"
    try:
        r = client.get(url)
        r.raise_for_status()
    except Exception as e:
        print(f"  [!] {acr}: failed to fetch Meetings index — {e}")
        return []
    meeting_nums = set()
    for m in re.finditer(
        rf"/DocumentViewer/en/{PARL_SESSION}/{acr}/meeting-(\d+)/evidence", r.text
    ):
        meeting_nums.add(int(m.group(1)))
    return sorted(meeting_nums)


def xml_url_for_meeting(client: httpx.Client, acr: str, meeting_n: int) -> str | None:
    """Fetch the meeting HTML and extract the direct Evidence XML URL."""
    meeting_html_url = (
        f"https://www.ourcommons.ca/DocumentViewer/en/{PARL_SESSION}/{acr}/"
        f"meeting-{meeting_n}/evidence"
    )
    try:
        r = client.get(meeting_html_url)
        r.raise_for_status()
    except Exception as e:
        print(f"    [!] {acr} meeting-{meeting_n}: HTML fetch failed — {e}")
        return None
    m = re.search(
        rf"(/Content/Committee/{PARL_SESSION_PATH}/{acr}/Evidence/EV\d+/{acr}EV\d+-E\.XML)",
        r.text,
        re.IGNORECASE,
    )
    if m:
        return "https://www.ourcommons.ca" + m.group(1)
    return None


def land_committee_xml(
    blob_service, client: httpx.Client, acr: str, meeting_n: int, xml_url: str
) -> LandingResult:
    now = datetime.now(timezone.utc)
    tested_at = now.isoformat()
    try:
        r = client.get(xml_url)
        r.raise_for_status()
    except Exception as e:
        return LandingResult(
            source_id="house-committee-transcripts",
            url=xml_url,
            ok=False,
            tested_at=tested_at,
            error=str(e),
            error_type=type(e).__name__,
            blocker_type="http_error",
            notes=f"{acr} meeting-{meeting_n}",
        )

    blob_path = (
        f"house-committee-transcripts/raw/{now.strftime('%Y-%m-%d')}/"
        f"{acr}_{PARL_SESSION}_meeting-{meeting_n:02d}.xml"
    )
    try:
        blob_client = blob_service.get_blob_client(
            container="polaris-bronze", blob=blob_path
        )
        blob_client.upload_blob(r.content, overwrite=True)
    except Exception as e:
        return LandingResult(
            source_id="house-committee-transcripts",
            url=xml_url,
            ok=False,
            tested_at=tested_at,
            bytes=len(r.content),
            error=str(e),
            error_type=type(e).__name__,
            blocker_type="storage_error",
            notes=f"{acr} meeting-{meeting_n}",
        )
    return LandingResult(
        source_id="house-committee-transcripts",
        url=xml_url,
        ok=True,
        tested_at=tested_at,
        http_status=r.status_code,
        content_type=r.headers.get("content-type"),
        bytes=len(r.content),
        blob_path=blob_path,
        notes=f"{acr} {PARL_SESSION} meeting-{meeting_n}",
    )


def main() -> None:
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok_count = 0
    fail_count = 0
    no_xml_count = 0
    skip_count = 0

    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for acr in COMMITTEES:
            print(f"\n=== {acr} ({PARL_SESSION}) ===")
            meetings = list_meetings_for_committee(client, acr)
            if not meetings:
                print(f"  no meetings found for {acr}")
                continue
            print(f"  meetings: {len(meetings)} -> {meetings[:5]}{'...' if len(meetings) > 5 else ''}")

            for n in meetings:
                time.sleep(0.4)  # polite rate limit
                xml_url = xml_url_for_meeting(client, acr, n)
                if not xml_url:
                    print(f"    meeting-{n:02d}  (no XML link on HTML page — in camera?)")
                    no_xml_count += 1
                    continue
                result = land_committee_xml(blob_service, client, acr, n, xml_url)
                append_result(result)
                if result.ok:
                    print(f"    meeting-{n:02d}  OK  {result.bytes:>8,} B")
                    ok_count += 1
                else:
                    print(f"    meeting-{n:02d}  FAIL {result.error_type}")
                    fail_count += 1

    print(f"\n=== Summary ===")
    print(f"  OK: {ok_count}")
    print(f"  FAIL: {fail_count}")
    print(f"  no XML (likely in camera): {no_xml_count}")
    print(f"  committees: {len(COMMITTEES)} across {PARL_SESSION}")


if __name__ == "__main__":
    main()
