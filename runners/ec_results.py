"""Access test: Elections Canada — Official Voting Results (44th GE, via CKAN).

Source: CKAN 065439a9-c194-4259-9c95-245a852be4a1
License: OGL-Canada 2.0
Flavor: B (dataset metadata; per-resource CSVs behind individual URLs)

Why 44th and not 45th: the 45th GE (April 2025) official results have not yet
been published to CKAN as of today. The 44th GE is the most recent available
dataset and proves the access path.

Phase 1 approach: land the CKAN package_show JSON. This gives us the full
resource list (6 summary CSVs + poll-by-poll references). Phase 2 enumerates
and fetches individual CSVs.

Run: `uv run python -m runners.ec_results`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-results-44"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=065439a9-c194-4259-9c95-245a852be4a1"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching CKAN metadata for 44th GE results ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="json",
        basename="package_show_44th_ge_results",
        browser_ua=True,
        notes=(
            "Phase 1 access test — CKAN metadata for 44th GE official voting results. "
            "Full CSVs enumerated via resource URLs in the response. "
            "45th GE results pending official publication by CEO."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
