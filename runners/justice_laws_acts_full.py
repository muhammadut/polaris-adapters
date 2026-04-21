"""Full Justice Laws enumeration — download every Act's individual XML.

The Legis.xml registry we already landed has 1,912 <Act> entries each with
a <LinkToXML> pointing to the per-Act full text. This runner fetches each.

Estimated: 1,912 fetches × ~100KB avg = ~200 MB, ~30-60 min at polite rate.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
import httpx
from lxml import etree
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}

    # Read the registry from Azure
    registry_blob = blob_service.get_blob_client(
        container="polaris-bronze",
        blob="justice-laws-acts/raw/2026-04-21/03-58-30_legis_registry.xml",
    )
    registry_xml = registry_blob.download_blob().readall()
    tree = etree.fromstring(registry_xml)
    acts = tree.findall(".//Act")
    print(f"Registry has {len(acts)} Acts to fetch", flush=True)

    ok = fail = skipped = 0
    with httpx.Client(timeout=60, follow_redirects=True, headers=headers) as client:
        for act in acts:
            unique_id = (act.findtext("UniqueId") or "").strip()
            link_to_xml = (act.findtext("LinkToXML") or "").strip()
            if not unique_id or not link_to_xml:
                skipped += 1
                continue
            # Upgrade http to https
            url = link_to_xml.replace("http://", "https://")

            now = datetime.now(timezone.utc)
            try:
                r = client.get(url)
                r.raise_for_status()
            except Exception as e:
                fail += 1
                if fail <= 10:
                    print(f"  [{unique_id}] FAIL {type(e).__name__}", flush=True)
                continue

            # Sanitize unique_id for filename (e.g., replace slashes, colons)
            safe_id = unique_id.replace("/", "_").replace(":", "_").replace(" ", "_")
            blob_path = f"justice-laws-acts/raw/2026-04-21/acts/{safe_id}.xml"
            try:
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            except Exception as e:
                fail += 1
                print(f"  [{unique_id}] STORAGE FAIL: {e}", flush=True)
                continue

            append_result(LandingResult(
                source_id="justice-laws-acts",
                url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, bytes=len(r.content), blob_path=blob_path,
                notes=f"Act {unique_id}",
            ))
            ok += 1
            if ok % 100 == 0:
                print(f"  progress: {ok} / {len(acts)} Acts landed", flush=True)
            time.sleep(0.3)

    print(f"\n=== Justice Laws Acts: {ok} OK, {fail} fail, {skipped} skipped ===", flush=True)


if __name__ == "__main__":
    main()
