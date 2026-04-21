"""Access test: OurCommons — Members of Parliament XML.

Source: https://www.ourcommons.ca/Members/en/search/xml
License: OGL-Canada 2.0
Flavor: A (clean structured XML API)
Expected: list of current MPs (343 in the 44th Parliament)

Run: `uv run python -m runners.ourcommons_mps`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ourcommons-mps"
URL = "https://www.ourcommons.ca/Members/en/search/xml"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        notes="Phase 1 access test — OurCommons MPs XML search endpoint",
    )

    if result.ok:
        print(f"[{SOURCE_ID}] OK — {result.bytes:,} bytes -> {result.blob_path}")
        print(f"               content-type: {result.content_type}")
    else:
        print(f"[{SOURCE_ID}] FAIL — {result.error_type}: {result.error}")
        print(f"               blocker: {result.blocker_type}")

    append_result(result)
    print(f"[{SOURCE_ID}] result appended to phase1-results.jsonl")


if __name__ == "__main__":
    main()
