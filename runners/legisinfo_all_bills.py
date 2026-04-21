"""LEGISinfo full bills enumeration — every bill across all parliaments in one JSON.

Endpoint returns an array of all bills. Each bill has the same 135-field
structure we already saw for the `recentlyintroduced` snapshot.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "legisinfo-all-bills"
URL = "https://www.parl.ca/legisinfo/en/bills/json"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="all_bills_allparliaments",
                 browser_ua=True, timeout_s=120,
                 notes="Every bill in LEGISinfo across all parliament-sessions, 135 fields each")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL'} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
