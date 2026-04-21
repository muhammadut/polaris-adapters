"""Access test: Office of the Commissioner of Lobbying — Monthly Communications (bulk ZIP).

Source: https://open.canada.ca/data/en/dataset/a34eb330-7136-4f5e-9f5f-3ba41df58b06
License: OGL-Canada 2.0
Flavor: B (bulk CSV in ZIP)
Expected: every oral-communication report between registered lobbyists and DPOHs — 10-20K/year

Run: `uv run python -m runners.federal_lobby_communications`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "federal-lobby-communications"
URL = "https://lobbycanada.gc.ca/media/mqbbmaqk/communications_ocl_cal.zip"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching bulk ZIP from {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="zip",
        basename="communications_bulk",
        browser_ua=True,
        timeout_s=300,
        notes=(
            "Phase 1 access test — OCL monthly communication reports ZIP. "
            "Who met which DPOH (MP/minister/official) when, about what."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
