"""Library of Parliament — public website landing (research publications gateway)."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "library-of-parliament"
URL = "https://lop.parl.ca"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="public_website_home",
                 browser_ua=True,
                 notes="Phase 1 — LoP public website landing. Phase 2 enumerates publications/historical data links.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
