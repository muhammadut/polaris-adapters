"""Access test: Justice Laws — Consolidated federal Acts registry (XML).

Source: https://laws-lois.justice.gc.ca/eng/XML/Legis.xml
License: OGL-Canada 2.0
Flavor: A (XML)
Expected: registry/index of every consolidated federal Act with links to individual Act XML files

Run: `uv run python -m runners.justice_laws_acts`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "justice-laws-acts"
URL = "https://laws-lois.justice.gc.ca/eng/XML/Legis.xml"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        basename="legis_registry",
        notes="Phase 1 access test — Justice Laws registry of all consolidated Acts (~5MB)",
        timeout_s=90,
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
