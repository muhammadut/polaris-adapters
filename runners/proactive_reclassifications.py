"""Access test: Proactive Disclosure — Position Reclassifications (the federal
equivalent of executive-comp reporting — tracks when positions are reclassified).

CKAN: f132b8a6-abad-43d6-b6ad-2301e778b1b6  |  License: OGL-Canada 2.0
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "proactive-reclassifications"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=f132b8a6-abad-43d6-b6ad-2301e778b1b6"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="package_show",
                 browser_ua=True,
                 notes="Phase 1 CKAN metadata for position reclassifications (federal exec-comp proxy).")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
