"""Access test: Proactive Disclosure — Grants & Contributions (schema + discovery).

Source: CKAN dataset 432527ab-7aac-45b5-81d6-7597107a7013 on open.canada.ca
License: OGL-Canada 2.0
Flavor: B (bulk CSV) — bulk is 2.2GB, deferred to Phase 2 backfill.

Phase 1 approach: land the small JSON schema. Full CSV deferred.

Run: `uv run python -m runners.proactive_grants`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "proactive-grants"
URL = "https://open.canada.ca/data/recombinant-published-schema/grants.json"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching schema {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="json",
        basename="schema",
        browser_ua=True,
        notes=(
            "Phase 1 access test — CKAN schema for federal grants+contributions >$25K. "
            "Full 2.2GB CSV at dataset 432527ab... deferred to Phase 2 backfill."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
