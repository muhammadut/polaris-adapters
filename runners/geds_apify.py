"""Apify re-pull: GEDS (federal employee directory) JS-rendered home."""
from polaris.landing import append_result, land_apify_rendered

SOURCE_ID = "geds-rendered"
URL = "https://geds-sage.gc.ca/GEDS20/dist/app/"

def main():
    print(f"[{SOURCE_ID}] rendering {URL} via Apify (9s wait — SPA) ...")
    r = land_apify_rendered(
        SOURCE_ID, URL,
        basename="geds_app_rendered",
        wait_ms=9000,
        notes="Apify-rendered GEDS app (/GEDS20/dist/app/) with 9s wait. Capture the fully-hydrated Angular app.",
    )
    if r.ok:
        print(f"[{SOURCE_ID}] OK  {r.bytes:,} bytes -> {r.blob_path}")
    else:
        print(f"[{SOURCE_ID}] FAIL  {r.error_type}: {r.error}")
    append_result(r)

if __name__ == "__main__": main()
