"""Access test: GEDS (Government Electronic Directory Services) — federal employee directory.

All GEDS URLs return the same 5,732-byte HTML shell (likely JS SPA). No public
bulk API visible. Phase 2 will need Playwright or XHR endpoint discovery.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "geds"
URL = "https://geds-sage.gc.ca/en/GEDS"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="spa_shell",
                 browser_ua=True,
                 notes=("Phase 1 — GEDS appears to be a JS SPA shell (5.7 KB consistently). "
                        "No visible bulk endpoint. Phase 2 needs Playwright or XHR discovery."))
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
