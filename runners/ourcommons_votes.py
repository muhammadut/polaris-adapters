"""Access test: OurCommons — Votes / Divisions (XML index).

Source: https://www.ourcommons.ca/members/en/votes
License: OGL-Canada 2.0
Flavor: A (XML/JSON)
Expected: list of recorded divisions in current parliament

First guess: /members/en/votes/xml pattern.

Run: `uv run python -m runners.ourcommons_votes`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "ourcommons-votes"
URL = "https://www.ourcommons.ca/members/en/votes/xml"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        basename="votes_index",
        notes="Phase 1 access test — probing /members/en/votes/xml pattern",
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
        print(f"              content-type: {result.content_type}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
