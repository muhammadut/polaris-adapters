"""Historical EC donations 2000-2004 (CKAN metadata)."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-donations-2000-2004"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=af0b8907-8234-4fa3-b3be-f4406a9aacb8"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="package_show",
                 browser_ua=True,
                 notes="Historical donations 2000-2004 (candidate contributions)")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
