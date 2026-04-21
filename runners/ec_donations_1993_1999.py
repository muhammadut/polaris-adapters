"""Historical EC donations 1993-1999 (CKAN metadata)."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-donations-1993-1999"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=5153bc55-c186-42db-8188-918811d1077d"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="package_show",
                 browser_ua=True,
                 notes="Pre-2004 historical donations (candidate contributions 1993-1999)")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
