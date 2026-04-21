"""Fetch all 343 current MP profile pages — richer data than the basic roster.

The MPs XML we have is thin (name, party, riding, elected date). The per-MP
profile page at /Members/en/<PersonId> has ~181 KB of richer HTML: contact
info, committee memberships, biography, photo URL, social links, etc.

Critical for entity resolution in Phase 2.
"""
from __future__ import annotations
import time, re
from datetime import datetime, timezone
import httpx
from lxml import etree
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}

    # Read MPs XML from Azure
    mps_xml = blob_service.get_blob_client(
        container="polaris-bronze",
        blob="ourcommons-mps/raw/2026-04-21/03-25-53_xml.xml",
    ).download_blob().readall()
    tree = etree.fromstring(mps_xml)
    person_ids = [(el.findtext("PersonId"),
                   el.findtext("PersonOfficialFirstName") or "",
                   el.findtext("PersonOfficialLastName") or "")
                  for el in tree.iter("MemberOfParliament")]
    print(f"Fetching {len(person_ids)} MP profile pages ...", flush=True)

    ok = fail = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for pid, first, last in person_ids:
            if not pid: continue
            url = f"https://www.ourcommons.ca/Members/en/{pid}"
            now = datetime.now(timezone.utc)
            try:
                r = client.get(url); r.raise_for_status()
            except Exception as e:
                fail += 1
                if fail <= 5:
                    print(f"  [{pid}] FAIL {type(e).__name__}", flush=True)
                continue
            safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', f"{first}_{last}")[:50]
            blob_path = f"ourcommons-mp-profiles/raw/2026-04-21/{pid}_{safe_name}.html"
            blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            append_result(LandingResult(
                source_id="ourcommons-mp-profiles",
                url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                notes=f"MP profile {first} {last} (PersonId {pid})",
            ))
            ok += 1
            if ok % 50 == 0:
                print(f"  progress: {ok} / {len(person_ids)}", flush=True)
            time.sleep(0.25)

    print(f"\n=== MP profiles: {ok} OK, {fail} fail ===", flush=True)


if __name__ == "__main__":
    main()
