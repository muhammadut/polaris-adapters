"""Access test: OurCommons — Bills index (XML).

Source: https://www.ourcommons.ca/Bills/ (portal)
License: OGL-Canada 2.0
Flavor: A (structured XML)
Expected: list of bills currently before the House

First guess: /Bills/en/search/xml (by analogy with MPs endpoint). Fallback paths
documented if this fails.

Run: `uv run python -m runners.ourcommons_bills`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ourcommons-bills"
URL = "https://www.ourcommons.ca/Bills/en/search/xml"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        basename="bills_search",
        notes="Phase 1 access test — probing /Bills/en/search/xml pattern",
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
        print(f"              content-type: {result.content_type}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
