"""43rd General Election results (CKAN metadata)."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-results-43"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=199e5070-2fd5-49d3-aa21-aece08964d18"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="package_show",
                 browser_ua=True,
                 notes="43rd GE (Oct 2019) official voting results CKAN metadata — 13 resources")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
