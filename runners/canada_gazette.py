"""Access test: Canada Gazette — English home page.

Canada Gazette publishes new regulations (Part II) + public notices (Part I).
Justice Laws XML gives us the current-consolidated Acts; Gazette tracks
per-issue new enactments + amendments.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "canada-gazette"
URL = "https://gazette.gc.ca/accueil-home-eng.html"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="accueil_home_en",
                 browser_ua=True,
                 notes="Canada Gazette English home. Phase 2 enumerates Part I + Part II issue-by-issue.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
