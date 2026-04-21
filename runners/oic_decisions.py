"""Access test: Office of the Information Commissioner — Final reports (decisions).

License: OGL-Canada 2.0  |  Format: HTML
OIC rules on ATIP complaint cases; findings published as reports.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "oic-decisions"
URL = "https://www.oic-ci.gc.ca/en/decisions/final-reports"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="final_reports_index",
                 browser_ua=True,
                 notes="Phase 1 — OIC final-reports index. Phase 2 will enumerate individual reports.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
