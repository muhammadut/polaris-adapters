"""Canada Gazette — land the publications-eng index page."""
from polaris.landing import append_result, land_raw

SOURCE_ID = "canada-gazette"
URL = "https://gazette.gc.ca/rp-pr/publications-eng.html"

def main():
    r = land_raw(SOURCE_ID, URL, ext="html", basename="publications_index",
                 browser_ua=True,
                 notes="Canada Gazette publications index — Part I + Part II enumerable from here")
    print(f"[{SOURCE_ID}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL'}")
    append_result(r)

if __name__ == "__main__": main()
