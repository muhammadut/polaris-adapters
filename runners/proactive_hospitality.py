"""Access test: Proactive Disclosure — Hospitality Expenses (schema).

CKAN: b9f51ef4-4605-4ef2-8231-62a2edda1b54  |  License: OGL-Canada 2.0
Phase 1: land schema. Full CSV deferred (recombinant pattern).
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "proactive-hospitality"
URL = "https://open.canada.ca/data/recombinant-published-schema/hospitalityq.json"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="schema", browser_ua=True,
                 notes="Phase 1 schema for hospitality expenses. Full CSV deferred.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
