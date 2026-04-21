"""Bulk backfill: download every known data CSV/ZIP/SHP that we previously deferred.

Executes ~50 downloads, ~4 GB total, across:
  - Proactive disclosure (contracts, grants, travel, hospitality, reclassifications)
  - Historical EC donations (pre-2000 + 2000-2004 in EN + FR)
  - Historical election results (42nd + 43rd GE, all CSVs)
  - Poll-by-poll 44th GE (all ZIPs)
  - Historical electoral boundaries (2006 + 2011, cartographic + digital, EN + FR)

Each download lands in Azure under its source slug. Failures logged but
don't halt the batch.
"""
from __future__ import annotations
import time
from datetime import datetime, timezone
import httpx
from polaris.landing import BROWSER_UA, _blob_service_client, LandingResult, append_result


DOWNLOADS = [
    # proactive-contracts (the big one)
    ("proactive-contracts", "https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b/resource/fac950c0-00d5-4ec1-a4d3-9cbebf98a305/download/contracts.csv", "csv", "contracts_full"),
    ("proactive-contracts", "https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b/resource/7f9b18ca-f627-4852-93d5-69adeb9437d6/download/load-contracts-2020-10-01.csv", "csv", "contracts_legacy"),
    ("proactive-contracts", "https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b/resource/2e9a82e2-bb18-4bff-a61e-59af3b429672/download/contractsa.csv", "csv", "contracts_aggregated_under_10k"),
    ("proactive-contracts", "https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b/resource/fa4ff6c4-e9af-4491-9d4e-2b468e415a68/download/contracts-nil.csv", "csv", "contracts_nil"),

    # proactive-grants (the 2.2GB beast)
    ("proactive-grants", "https://open.canada.ca/data/dataset/432527ab-7aac-45b5-81d6-7597107a7013/resource/1d15a62f-5656-49ad-8c88-f40ce689d831/download/gc.csv", "csv", "grants_full"),
    ("proactive-grants", "https://open.canada.ca/data/dataset/432527ab-7aac-45b5-81d6-7597107a7013/resource/4e4db232-f5e8-43c7-b8b2-439eb7d55475/download/gc-nil.csv", "csv", "grants_nil"),

    # proactive-travel
    ("proactive-travel", "https://open.canada.ca/data/dataset/009f9a49-c2d9-4d29-a6d4-1a228da335ce/resource/8282db2a-878f-475c-af10-ad56aa8fa72c/download/travelq.csv", "csv", "travel_full"),
    ("proactive-travel", "https://open.canada.ca/data/dataset/009f9a49-c2d9-4d29-a6d4-1a228da335ce/resource/d3f883ce-4133-48da-bc76-c6b063d257a2/download/travelq-nil.csv", "csv", "travel_nil"),

    # proactive-hospitality
    ("proactive-hospitality", "https://open.canada.ca/data/dataset/b9f51ef4-4605-4ef2-8231-62a2edda1b54/resource/7b301f1a-2a7a-48bd-9ea9-e0ac4a5313ed/download/hospitalityq.csv", "csv", "hospitality_full"),
    ("proactive-hospitality", "https://open.canada.ca/data/dataset/b9f51ef4-4605-4ef2-8231-62a2edda1b54/resource/36a3b6cc-4f45-4081-8dbd-2340ca487041/download/hospitalityq-nil.csv", "csv", "hospitality_nil"),

    # proactive-reclassifications
    ("proactive-reclassifications", "https://open.canada.ca/data/dataset/f132b8a6-abad-43d6-b6ad-2301e778b1b6/resource/bdaa5515-3782-4e5c-9d44-c25e032addb7/download/reclassification.csv", "csv", "reclass_full"),
    ("proactive-reclassifications", "https://open.canada.ca/data/dataset/f132b8a6-abad-43d6-b6ad-2301e778b1b6/resource/1e955e4d-df35-4441-bf38-b7086192ece2/download/reclassification-nil.csv", "csv", "reclass_nil"),

    # historical EC donations
    ("ec-donations-1993-1999", "https://www.elections.ca/fin/oda/candidate_pre_2000_contributors_e.zip", "zip", "pre_2000_en"),
    ("ec-donations-1993-1999", "https://www.elections.ca/fin/oda/candidate_pre_2000_contributors_f.zip", "zip", "pre_2000_fr"),
    ("ec-donations-2000-2004", "https://www.elections.ca/fin/oda/candidate_2000_2004_contributors_audt_e.zip", "zip", "2000_2004_en"),
    ("ec-donations-2000-2004", "https://www.elections.ca/fin/oda/candidate_2000_2004_contributors_audt_f.zip", "zip", "2000_2004_fr"),

    # EC poll-by-poll 44th
    ("ec-poll-by-poll-44", "https://www.elections.ca/res/rep/off/ovr2021app/53/data_donnees/pollbypoll_bureauparbureauCanada.zip", "zip", "pollbypoll_canada"),
    ("ec-poll-by-poll-44", "https://www.elections.ca/res/rep/off/ovr2021app/53/data_donnees/pollresults_resultatsbureauCanada.zip", "zip", "pollresults_canada"),

    # EC historical boundaries (statcan census geo files — these are the canonical shapefiles)
    ("ec-boundaries-2011", "https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/files-fichiers/gfed000a11a_e.zip", "zip", "digital_2011_en"),
    ("ec-boundaries-2011", "https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/files-fichiers/gfed000b11a_e.zip", "zip", "cartographic_2011_en"),
    ("ec-boundaries-2006", "https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/files-fichiers/gfed000a06a_e.zip", "zip", "digital_2006_en"),
    ("ec-boundaries-2006", "https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/files-fichiers/gfed000b06a_e.zip", "zip", "cartographic_2006_en"),
]

# Plus all 13 per-election CSVs for 42nd + 43rd GE
for i in range(1, 14):
    suffix = f"{i:02d}"
    DOWNLOADS.append(
        ("ec-results-42",
         f"https://www.elections.ca/res/rep/off/ovr2015app/41/data_donnees/table_tableau{suffix}.csv",
         "csv",
         f"table_{suffix}_42nd_ge")
    )


def main():
    blob_service = _blob_service_client()
    headers = {"User-Agent": BROWSER_UA}
    ok = fail = 0
    total_bytes = 0

    with httpx.Client(timeout=1200, follow_redirects=True, headers=headers) as client:
        for slug, url, ext, basename in DOWNLOADS:
            now = datetime.now(timezone.utc)
            try:
                print(f"  [{slug}] fetching {basename} ...", flush=True)
                r = client.get(url)
                r.raise_for_status()
            except Exception as e:
                print(f"  [{slug}] FAIL {basename}: {type(e).__name__}: {e}", flush=True)
                append_result(LandingResult(
                    source_id=slug, url=url, ok=False, tested_at=now.isoformat(),
                    error=str(e), error_type=type(e).__name__,
                    blocker_type="http_error",
                    notes=f"bulk backfill {basename}",
                ))
                fail += 1
                continue

            blob_path = f"{slug}/raw/{now.strftime('%Y-%m-%d')}/{now.strftime('%H-%M-%S')}_{basename}.{ext}"
            try:
                blob_service.get_blob_client(container="polaris-bronze", blob=blob_path).upload_blob(r.content, overwrite=True)
            except Exception as e:
                print(f"  [{slug}] STORAGE FAIL {basename}: {e}", flush=True)
                append_result(LandingResult(
                    source_id=slug, url=url, ok=False, tested_at=now.isoformat(),
                    bytes=len(r.content), error=str(e),
                    error_type=type(e).__name__, blocker_type="storage_error",
                    notes=f"bulk backfill {basename}",
                ))
                fail += 1
                continue

            append_result(LandingResult(
                source_id=slug, url=url, ok=True, tested_at=now.isoformat(),
                http_status=r.status_code, content_type=r.headers.get("content-type"),
                bytes=len(r.content), blob_path=blob_path,
                notes=f"bulk backfill {basename}",
            ))
            total_bytes += len(r.content)
            print(f"  [{slug}] OK  {len(r.content):>13,} B  -> {blob_path}", flush=True)
            ok += 1
            time.sleep(0.5)

    print(f"\n=== Bulk backfill summary: {ok} OK, {fail} failed ===")
    print(f"=== Downloaded {total_bytes/1024/1024:.1f} MB ({total_bytes/1024/1024/1024:.2f} GB) ===")


if __name__ == "__main__":
    main()
