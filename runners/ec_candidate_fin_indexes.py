"""Land the EC candidate financial index pages.

These are the entry points from which per-candidate financial returns
are navigated. Full per-candidate scrape is a focused follow-up job.
"""
from polaris.landing import append_result, land_raw

INDEXES = [
    ("ec-candidates-fin",  "https://www.elections.ca/content.aspx?section=pol&dir=can/fin&document=index&lang=e",  "fin_index"),
    ("ec-candidates-rep",  "https://www.elections.ca/content.aspx?section=pol&dir=can/rep&document=index&lang=e",  "reports_index"),
    ("ec-candidates-res",  "https://www.elections.ca/content.aspx?section=pol&dir=can/res&document=index&lang=e",  "results_index"),
    ("ec-candidates-sub",  "https://www.elections.ca/content.aspx?section=pol&dir=can/sub&document=index&lang=e",  "submissions_index"),
    ("ec-financial-reports", "https://www.elections.ca/WPAPPS/WPF/EN/CCS/FinancialReports",                        "ccs_financial_reports"),
]

def main():
    for slug, url, basename in INDEXES:
        r = land_raw(slug, url, ext="html", basename=basename, browser_ua=True,
                     notes="EC candidate financial navigation entry")
        print(f"[{slug}] {'OK '+str(r.bytes)+'B' if r.ok else 'FAIL'}")
        append_result(r)

if __name__ == "__main__": main()
