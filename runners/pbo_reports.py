"""Access test: Parliamentary Budget Officer — publications index.

Source: https://www.pbo-dpb.ca/en/publications
License: OGL-Canada 2.0 (PBO is an independent Officer of Parliament)
Flavor: D-heavy (HTML/JS — publications page appears to be SPA; no PDF
list in static HTML, no sitemap, no API found)

Phase 1 approach: land the publications index HTML so Phase 2 has something
to diff against. Real PBO ingest will require Playwright to render JS or a
different discovery path (maybe the publications RSS feed — to probe).

Run: `uv run python -m runners.pbo_reports`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "pbo-reports"
URL = "https://www.pbo-dpb.ca/en/publications"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="html",
        basename="publications_index",
        browser_ua=True,
        notes=(
            "Phase 1 access test — PBO publications index HTML (17 KB, likely "
            "JS-rendered SPA). No visible PDF links in static HTML, no sitemap, "
            "no documented API. Phase 2 will need Playwright for rendering "
            "or RSS feed probing."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
