"""Poll-by-poll results for the 44th General Election (detailed per-polling-station)."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-poll-by-poll-44"
URL = "https://open.canada.ca/data/en/api/3/action/package_show?id=d5512235-cfb2-4ccf-a886-547913f4aa52"

def main():
    r = land_raw(SOURCE_ID, URL, ext="json", basename="package_show",
                 browser_ua=True,
                 notes="Poll-by-poll detail for 44th GE — finest-grain results (6 resources)")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
