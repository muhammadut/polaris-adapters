"""Access test: Office of the Commissioner of Lobbying — Registrations (bulk ZIP).

Source: https://lobbycanada.gc.ca/en/open-data/
License: OGL-Canada 2.0
Flavor: B (bulk CSV in ZIP)
Expected: full historical + active registrations — ~3,000 active + deep history

Run: `uv run python -m runners.federal_lobby_registrations`
"""

from __future__ import annotations

from polaris.landing import append_result, land_raw

SOURCE_ID = "federal-lobby-registrations"
URL = "https://lobbycanada.gc.ca/media/zwcjycef/registrations_enregistrements_ocl_cal.zip"


def main() -> None:
    print(f"[{SOURCE_ID}] fetching bulk ZIP from {URL} ...")
    result = land_raw(
        SOURCE_ID,
        URL,
        ext="zip",
        basename="registrations_bulk",
        browser_ua=True,
        timeout_s=300,
        notes=(
            "Phase 1 access test — OCL full lobbying registrations ZIP. "
            "Core moat data: clients × lobbyists × subjects × institutions."
        ),
    )
    if result.ok:
        print(f"[{SOURCE_ID}] OK  {result.bytes:,} bytes -> {result.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {result.error_type}: {result.error}")
    append_result(result)


if __name__ == "__main__":
    main()
