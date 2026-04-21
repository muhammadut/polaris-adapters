"""Access test: Elections Canada — Registered Political Parties (HTML index).

License: OGL-Canada 2.0  |  Format: HTML (financial reports are sub-page PDFs)
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "ec-registered-parties"
URL = "https://www.elections.ca/content.aspx?section=pol&dir=par&document=index&lang=e"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="parties_index",
                 browser_ua=True,
                 notes="Phase 1 — Registered parties index. Phase 2 enumerates per-party financial reports.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
