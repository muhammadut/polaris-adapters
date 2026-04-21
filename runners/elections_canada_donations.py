"""Access test: Elections Canada — Contributions to all political entities (bulk).

Source: Elections Canada political financing, published on both elections.ca and open.canada.ca
License: OGL-Canada 2.0 (open.canada.ca indexed)
Flavor: B (bulk ZIP containing CSVs)
Expected: ~115 MB ZIP, English columns

Run: `uv run python -m runners.elections_canada_donations`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "elections-canada-donations"
URL = "https://www.elections.ca/fin/oda/od_cntrbtn_audt_e.zip"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching 115MB ZIP from {URL} ...")
    print("  (this takes ~30s-2min depending on network)")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="zip",
        basename="contributions_all_entities_en",
        browser_ua=True,
        timeout_s=600,  # 10 minutes for a 115 MB download
        notes="Phase 1 access test — Elections Canada all-political-entity contributions ZIP (115MB)",
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
