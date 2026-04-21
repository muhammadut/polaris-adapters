"""Access test: Senate Hansard (Debates) — latest sitting (HTML).

Source: https://sencanada.ca/en/in-the-chamber/debates/
License: OGL-Canada 2.0
Flavor: D (HTML only — no XML endpoint exists)

Phase 1: land one recent sitting day's HTML. Phase 2 will enumerate debate
URLs from the index page and scrape each + LLM-extract into the canonical
`speech` table.

Chosen sample: debate 064, 2026-04-16 (45th Parliament, 1st session), URL
discovered by scraping the debates index.

Run: `uv run python -m runners.senate_hansard`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "senate-hansard"
URL = "https://sencanada.ca/en/content/sen/chamber/451/debates/064db_2026-04-16-e"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="html",
        basename="debate_064_2026-04-16",
        browser_ua=True,
        notes=(
            "Phase 1 access test — Senate Hansard for sitting 064 (2026-04-16) 45-1. "
            "HTML only — Senate does NOT expose chamber debates as XML (all /xml "
            "variants 404). Phase 2 will HTML-scrape + LLM-extract speeches."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
