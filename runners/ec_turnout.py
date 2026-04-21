"""Access test: Elections Canada — Voter Turnout (HTML).

Source: https://www.elections.ca/content.aspx?section=ele&dir=turn&document=index&lang=e
License: OGL-Canada 2.0
Flavor: D (HTML — no CSV download; turnout tables are rendered in-page)
Expected: national + by-province turnout tables for every GE since 2004

Phase 2: parse HTML tables with BeautifulSoup + pandas; enrich with
age/sex breakdowns from the per-GE sub-pages.

Run: `uv run python -m runners.ec_turnout`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-turnout"
URL = "https://www.elections.ca/content.aspx?section=ele&dir=turn&document=index&lang=e"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="html",
        basename="turnout_index",
        browser_ua=True,
        notes=(
            "Phase 1 access test — turnout index HTML. "
            "No CSV downloads on this page; turnout data embedded in HTML tables. "
            "Phase 2 will parse tables + fetch per-GE sub-pages."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
