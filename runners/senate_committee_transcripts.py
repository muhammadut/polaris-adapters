"""Access test: Senate Committee Transcripts — HTML (sample).

Source pattern: https://sencanada.ca/en/committees/<acronym>/<parl>-<sess>
License: OGL-Canada 2.0
Flavor: D (HTML — Senate does NOT expose committee transcripts as XML)

Phase 1 sample: Standing Senate Committee on Banking, Commerce and the
Economy (BANC), 45-1.

Phase 2 will enumerate all Senate committees × all meetings and HTML-scrape
each page. Senate committees are a harder target than House because no
XML is available — more LLM extraction required.

Run: `uv run python -m runners.senate_committee_transcripts`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "senate-committee-transcripts"
URL = "https://sencanada.ca/en/committees/banc/45-1"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="html",
        basename="BANC_45-1_landing",
        browser_ua=True,
        notes=(
            "Phase 1 access test — Senate BANC (Banking Commerce Economy) 45-1 page. "
            "HTML landing only. Senate committee transcripts are HTML-only; "
            "Phase 2 will require Playwright + LLM extraction for structured speech data."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
