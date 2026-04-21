"""Access test: Office of the Privacy Commissioner — findings (investigations into businesses).

License: OGL-Canada 2.0  |  Format: HTML
OPC investigates privacy complaints under PIPEDA + Privacy Act; findings listed per year.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "opc-findings"
URL = "https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="investigations_index",
                 browser_ua=True,
                 notes="Phase 1 — OPC business investigations index. Phase 2 enumerates individual findings.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
