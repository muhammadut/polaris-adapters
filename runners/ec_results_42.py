"""42nd General Election results (CKAN metadata)."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-results-42"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=775f3136-1aa3-4854-a51e-1a2dab362525"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="package_show",
                 browser_ua=True,
                 notes="42nd GE (Oct 2015) official voting results CKAN metadata — 13 resources")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
