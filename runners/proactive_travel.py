"""Access test: Proactive Disclosure — Travel Expenses (schema + discovery).

CKAN: 009f9a49-c2d9-4d29-a6d4-1a228da335ce  |  License: OGL-Canada 2.0
Phase 1: land schema (bulk CSV follows recombinant pattern, deferred).
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "proactive-travel"
URL = "https://open.canada.ca/data/recombinant-published-schema/travelq.json"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="schema", browser_ua=True,
                 notes="Phase 1 schema for travel expenses. Full CSV deferred.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
