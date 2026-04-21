"""Apify re-pull: OAG — render the gateway to discover the actual report URL structure.

Previously only landed the 4 KB meta-refresh gateway. This run renders the
gateway (which may immediately redirect via JS to the actual English site)
and captures whatever the browser ends up showing.
"""
from polaris.landing import append_result, land_apify_rendered

SOURCE_ID = "auditor-general-reports-rendered"
URL = "https://www.oag-bvg.gc.ca/internet/index.htm"

def main():
    print(f"[{SOURCE_ID}] rendering {URL} via Apify (9s wait — JS-heavy site) ...")
    r = land_apify_rendered(
        SOURCE_ID, URL,
        basename="oag_index_rendered",
        wait_ms=9000,
        notes="Apify-rendered OAG gateway with 9s JS wait. Capture the real site content after client-side rendering.",
    )
    if r.ok:
        print(f"[{SOURCE_ID}] OK  {r.bytes:,} bytes -> {r.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {r.error_type}: {r.error}")
    append_result(r)

if __name__ == "__main__": main()
