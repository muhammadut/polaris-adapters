"""Access test: Federal Hansard — historical backfill proof (44-1 sitting 1).

Confirms the URL pattern /Content/House/<parl><sess>/Debates/<NN>/HAN<NN>-E.XML works
for prior parliaments — Phase 2 will enumerate all sitting days across 44-1, 43-1, etc.
"""
from polaris.landing import append_result, land_raw

SOURCE_ID = "federal-hansard-house-historical"
URL = "https://www.ourcommons.ca/Content/House/441/Debates/001/HAN001-E.XML"

def main():
    r = land_raw(SOURCE_ID, URL, ext="xml", basename="HAN441_day001",
                 timeout_s=60,
                 notes="Phase 1 historical proof — Hansard 44-1 sitting day 1. Pattern works for backfill.")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL '+str(r.error)} -> {r.blob_path}")
    append_result(r)

if __name__ == "__main__": main()
