"""Historical electoral boundary datasets (CKAN metadata for 2006, 2011).

We have 2025 boundaries already as the actual SHP bundle. These are
CKAN metadata for the 2006 and 2011 Census-era boundary files — useful
for retrospective postal-code → riding lookups across election vintages.
"""
from polaris.landing import append_result, land_raw

DATASETS = [
    ("ec-boundaries-2006-cartographic", "bcdb6685-c1cf-4664-8b4e-63dc9e6921c5"),
    ("ec-boundaries-2006-digital",      "7e2e7c67-d6dc-4dbb-944e-a52dba5a1a89"),
    ("ec-boundaries-2011-cartographic", "69abc973-412b-4150-bd2f-3131186c4ee4"),
    ("ec-boundaries-2011-digital",      "48f10fb9-78a2-43a9-92ab-354c28d30674"),
]

def main():
    for slug, did in DATASETS:
        url = f"https://open.canada.ca/data/en/api/3/action/package_show?id={did}"
        r = land_raw(slug, url, ext="json", basename="package_show",
                     browser_ua=True,
                     notes=f"Historical boundaries CKAN metadata ({slug})")
        print(f"[{slug}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL'}")
        append_result(r)

if __name__ == "__main__": main()
