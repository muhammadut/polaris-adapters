"""Access test: PCO Mandate Letter Tracker — ministerial commitments.

CKAN: 8f6b5490-8684-4a0d-91a3-97ba28acc9cd  |  License: OGL-Canada 2.0
Direct CSV URL available.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "pco-mandate-letters"
URL = "https://opendata.pco.gc.ca/data-donnees/rdu-url/mandat/commitments-engagements-eng.csv"

def main():
    r = land_raw(SOURCE_ID, URL, ext="csv", basename="commitments_engagements_en",
                 browser_ua=True, timeout_s=120,
                 notes="Phase 1 direct CSV — mandate letter commitments per minister.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
