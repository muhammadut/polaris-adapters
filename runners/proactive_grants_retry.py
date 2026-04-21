"""Retry: proactive-grants bulk CSVs (actual URL is /grants.csv, not /gc.csv)."""
from polaris.landing import append_result, land_raw

URLS = [
    ("proactive-grants", "https://open.canada.ca/data/dataset/432527ab-7aac-45b5-81d6-7597107a7013/resource/1d15a62f-5656-49ad-8c88-f40ce689d831/download/grants.csv", "grants_full"),
    ("proactive-grants", "https://open.canada.ca/data/dataset/432527ab-7aac-45b5-81d6-7597107a7013/resource/4e4db232-f5e8-43c7-b8b2-439eb7d55475/download/grants-nil.csv", "grants_nil"),
]

def main():
    for slug, url, basename in URLS:
        print(f"[{slug}] fetching {basename} (2.2 GB if grants_full) ...", flush=True)
        r = land_raw(slug, url, ext="csv", basename=basename, browser_ua=True,
                     timeout_s=1200, notes=f"bulk backfill retry {basename}")
        if r.ok:
            print(f"[{slug}] OK {r.bytes:,} B -> {r.blob_path}", flush=True)
        else:
            print(f"[{slug}] FAIL {r.error_type}: {r.error}", flush=True)
        append_result(r)

if __name__ == "__main__":
    main()
