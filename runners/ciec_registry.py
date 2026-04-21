"""Access test: Conflict of Interest and Ethics Commissioner — Public Registry (federal).

License: OGL-Canada 2.0  |  Format: HTML-only
Covers MP + public office holder asset disclosures, gifts, outside activities.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ciec-registry"
URL = "https://prciec-rpccie.parl.gc.ca/EN/PublicRegistries/Pages/PublicRegistryHome.aspx"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="public_registry_home",
                 browser_ua=True,
                 notes="Phase 1 — CIEC public registry home. Phase 2 needs Playwright scrape for individual disclosures.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
