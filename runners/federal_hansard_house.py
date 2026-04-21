"""Access test: Federal Hansard — House of Commons Debates XML (latest sitting day).

Source: https://www.ourcommons.ca/Content/House/<parl><sess>/Debates/<N>/HAN<N>-E.XML
License: OGL-Canada 2.0
Flavor: C (XML per sitting day) — multi-URL pattern

Phase 1: land the latest sitting day (HAN105-E.XML for 45th Parliament session 1
as of 2026-04-15, discovered via the `/DocumentViewer/en/house/latest/hansard`
portal HTML which embeds the XML link).

Phase 2: build a sitting-day enumerator to backfill all days.

Run: `uv run python -m runners.federal_hansard_house`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "federal-hansard-house"
URL = "https://www.ourcommons.ca/Content/House/451/Debates/105/HAN105-E.XML"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        basename="HAN105-E",
        timeout_s=120,
        notes=(
            "Phase 1 access test — House Hansard XML for 45-1 sitting 105. "
            "Phase 2 needs a sitting-day enumerator to backfill earlier days."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
