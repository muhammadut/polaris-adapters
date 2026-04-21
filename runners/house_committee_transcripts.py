"""Access test: House Committee Transcripts — Evidence XML (sample).

Source pattern: https://www.ourcommons.ca/Content/Committee/<parl><sess>/<ACR>/Evidence/EV<id>/<ACR>EV<N>-E.XML
License: OGL-Canada 2.0
Flavor: C (structured XML per meeting, but multi-URL discovery required)

Phase 1 sample: Standing Committee on Finance (FINA), meeting 1 of 45-1.
URL discovered by scraping the meeting HTML page for the embedded XML link.

Phase 2 will enumerate all committees × all meetings × evidence XML by
scraping the Meetings index page per committee.

Run: `uv run python -m runners.house_committee_transcripts`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "house-committee-transcripts"
URL = "https://www.ourcommons.ca/Content/Committee/451/FINA/Evidence/EV13563616/FINAEV01-E.XML"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="xml",
        basename="FINA_45-1_EV01",
        notes=(
            "Phase 1 access test — House FINA Committee Evidence meeting 1 (45-1). "
            "XML works when the /xml-suffix doesn't. Phase 2 will enumerate all "
            "committees × meetings. ~25 standing committees + specials."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
