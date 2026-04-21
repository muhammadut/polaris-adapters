"""Access test: Board of Internal Economy — MP expenses reports.

License: OGL-Canada 2.0  |  Format: HTML (probably PDFs linked within)
BOIE publishes MP office + travel expenses quarterly.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "boie-mp-expenses"
URL = "https://www.ourcommons.ca/boie/en/reports"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="reports_index",
                 notes="Phase 1 — BOIE reports index (MP expenses). Phase 2 will parse linked PDFs/CSVs.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
