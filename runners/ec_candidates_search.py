"""Access proof: Elections Canada Candidate & Financial Summary (CCS) search portal.

This is the gateway to per-candidate financial returns. Returns are NOT on a
simple index — they're retrieved via form POST with candidate/election filters,
then downloaded as PDFs.

Phase 1 lands the search page HTML as an access proof.
Phase 2 requires form-submission automation (Playwright/Apify with formData)
to enumerate all candidates across 42nd/43rd/44th GEs (~5,000 returns total).
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-candidates-search"
URL = "https://www.elections.ca/WPAPPS/WPF/EN/CCS/Search"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="ccs_search_portal",
                 browser_ua=True,
                 notes="EC Contributions & Financial Summary search portal. Phase 2 form-submit per candidate.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
