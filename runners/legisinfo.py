"""Access test: LEGISinfo — federal bill status tracker (JSON).

Source: https://www.parl.ca/legisinfo/en/overview/json/recentlyintroduced
License: OGL-Canada 2.0
Flavor: A (clean JSON API)
Expected: array of recently introduced bills with status metadata

Run: `uv run python -m runners.legisinfo`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "legisinfo"
URL = "https://www.parl.ca/legisinfo/en/overview/json/recentlyintroduced"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="json",
        basename="recentlyintroduced",
        notes="Phase 1 access test — LEGISinfo recently introduced bills (JSON overview)",
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
        print(f"              content-type: {result.content_type}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
