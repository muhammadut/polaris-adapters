"""Access test: Elections Canada — Electoral Boundaries (45th GE shapefile).

Source: CKAN 97a2a33c-54cc-4f2e-82c1-047ad8212f05 (OGL-Canada 2.0)
Flavor: B (bulk geospatial ZIP)
Format: ESRI Shapefile (ZIP bundle containing .shp, .dbf, .prj, .shx)
Expected: the 338 federal electoral districts for the 45th General Election (2025)

Run: `uv run python -m runners.ec_boundaries_45`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-boundaries-45"
URL = "https://www.elections.ca/res/cir/mapsCorner/vector/FederalElectoralDistricts_2025_SHP.zip"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching shapefile ZIP from {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="zip",
        basename="federal_electoral_districts_2025_shp",
        browser_ua=True,
        timeout_s=300,
        notes=(
            "Phase 1 access test — 45th GE federal electoral district boundaries, ESRI Shapefile. "
            "Foundation for postal-code→riding lookups and every geographic rollup."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
