"""Apify re-pull: PBO publications page (JS-rendered).

Previously landed the 17 KB SPA shell. This run renders the page in headless
Chrome (waits 5s for the React app to hydrate + fetch publications), captures
the full DOM, and lands it.
"""
from polaris.landing import append_result, land_apify_rendered

SOURCE_ID = "pbo-reports-rendered"
URL = "https://www.pbo-dpb.ca/en/publications"

def main():
    print(f"[{SOURCE_ID}] rendering {URL} via Apify ...")
    r = land_apify_rendered(
        SOURCE_ID, URL,
        basename="publications_rendered",
        wait_ms=5000,
        notes="Apify-rendered PBO publications page (JS SPA). Phase 2 parses for publication links + PDFs.",
    )
    if r.ok:
        print(f"[{SOURCE_ID}] OK  {r.bytes:,} bytes -> {r.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {r.error_type}: {r.error}")
    append_result(r)

if __name__ == "__main__": main()
