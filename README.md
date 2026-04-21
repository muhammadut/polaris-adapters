# polaris-adapters

Phase 1 of Polaris: access-test every Canadian political data source and land raw bytes in Azure Blob Storage. No schema, no parsing, no entity resolution — that's Phase 2 and later.

**Parent docs:** [`../polaris/`](../polaris/) — the planning/strategy directory.

## Quick start

```bash
# One-time: copy creds into local .env (see .env.example)
cp .env.example .env
# ...fill in values

# Run one access test
uv run python -m runners.ourcommons_mps

# Result lands in Azure Blob Storage at:
#   polaris-bronze/ourcommons-mps/raw/<YYYY-MM-DD>/<HH-MM-SS>_search.xml

# And is appended as one line to phase1-results.jsonl
```

## Layout

```
polaris-adapters/
├── polaris/
│   ├── __init__.py
│   └── landing.py              # land_raw() — the one function every test calls
├── runners/
│   ├── __init__.py
│   └── ourcommons_mps.py       # one file per source-under-test
├── phase1-results.jsonl        # append-only log, one row per test run
├── .env                        # creds, gitignored
└── .env.example                # template, committed
```

## Adding a new source

Copy `runners/ourcommons_mps.py` to `runners/<source_slug>.py`. Change three things:

1. `SOURCE_ID` — the slug from `../polaris/political-sources-catalog.md`
2. `URL` — the starting endpoint
3. `ext` — file extension (`xml`, `json`, `csv`, `html`, `pdf`)

Run `uv run python -m runners.<source_slug>`. Done.

## Azure resources

See `../polaris/` memory and decision log. Subscription `Primary`, RG `rg-polaris-dev-data`, storage `stpolarisdev2515`, container `polaris-bronze`.

## Status

Phase 1 in progress. See `phase1-results.jsonl` for what's been tested.
