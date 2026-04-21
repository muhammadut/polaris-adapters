"""Access test: OurCommons — Committees (XML index).

Source: https://www.ourcommons.ca/Committees/en
License: OGL-Canada 2.0
Flavor: A (structured XML)
Expected: list of House standing + special committees

First guess: /Committees/en/search/xml by analogy with MPs endpoint.

Run: `uv run python -m runners.ourcommons_committees`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ourcommons-committees"
URL = "https://www.ourcommons.ca/Committees/en/List"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="html",
        basename="committees_list",
        notes=(
            "Phase 1 access test — HTML list page. No XML endpoint exists (verified: "
            "/Committees/en/List/xml, /Committees/en/home/xml, /Committees/en/44-1/xml "
            "all 404). Phase 2 will scrape this HTML + fetch per-committee acronym pages."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
        print(f"              content-type: {result.content_type}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
