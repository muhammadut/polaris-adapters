"""Access test: Consolidated Canadian Autonomous Sanctions List (SEMA + JVCFOA).

Source: https://www.international.gc.ca/world-monde/international_relations-relations_internationales/sanctions/consolidated-consolide.aspx?lang=eng
License: OGL-Canada 2.0
Flavor: A (XML) — link discovered on the HTML consolidated list page
Expected: all individuals + entities sanctioned under SEMA and JVCFOA (names, aliases, DOBs, basis)

Run: `uv run python -m runners.sanctions_consolidated`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "sanctions-consolidated"
URL = "https://www.international.gc.ca/world-monde/assets/office_docs/international_relations-relations_internationales/sanctions/sema-lmes.xml"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        basename="sema_lmes",
        browser_ua=True,
        notes="Phase 1 access test — SEMA+JVCFOA consolidated sanctions XML",
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
