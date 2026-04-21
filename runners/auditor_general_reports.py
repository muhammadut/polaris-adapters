"""Access test: Auditor General of Canada — publications landing.

Note: oag-bvg.gc.ca returns a 404-style page for every URL we've tried. The site
may use a JS-rendered discovery layer or the URL structure is non-obvious. The
only URL that returns distinct content is the English gateway /internet/index.htm.
Phase 2 will need Playwright + sitemap discovery OR direct PDF URL probing
with a better pattern.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "auditor-general-reports"
URL = "https://www.oag-bvg.gc.ca/internet/index.htm"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="gateway",
                 browser_ua=True,
                 notes=("Phase 1 access test — OAG English gateway (meta-refresh redirect target). "
                        "Deeper URLs all return a 'not found' page despite HTTP 200. "
                        "Phase 2 needs Playwright or direct PDF URL discovery."))
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
