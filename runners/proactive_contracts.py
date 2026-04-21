"""Access test: Proactive Disclosure — Contracts (schema + discovery).

Source: CKAN dataset d8f85d91-7dec-4fd1-8055-483b77225d8b on open.canada.ca
License: OGL-Canada 2.0
Flavor: B (bulk CSV) — but the bulk CSV is 610MB, deferred to Phase 2 backfill.

Phase 1 approach: land the small JSON schema that describes the columns.
The full 610MB contracts CSV is at:
  https://open.canada.ca/data/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b/resource/fac950c0-00d5-4ec1-a4d3-9cbebf98a305/download/contracts.csv

Run: `uv run python -m runners.proactive_contracts`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "proactive-contracts"
URL = "https://open.canada.ca/data/recombinant-published-schema/contracts.json"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching schema {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="json",
        basename="schema",
        browser_ua=True,
        notes=(
            "Phase 1 access test — CKAN schema for federal contracts >$10K. "
            "Full 610MB CSV at /dataset/d8f85d91.../resource/fac950c0.../download/contracts.csv "
            "deferred to Phase 2 backfill."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
