# Scrapling deal ingestion

This is a **candidate collector**, not an automated publisher. It reads retailer listing pages using [Scrapling](https://github.com/D4Vinci/Scrapling) and generates a separate JSON file containing candidate deals for editorial review. It never changes `sites/*/src/data/deals.json`, affiliate links, or existing approvals.

## Local fixture demo (no network)

Use Python 3.12+ and install the pinned parser:

```bash
python -m pip install 'scrapling==0.5.1'
python -m unittest discover -s scraper/tests -v
python -m scraper.collector --config scraper/examples/fixture-source.json --output /tmp/deal-candidates.json
```

Inspect `/tmp/deal-candidates.json`. The fixture contains two valid candidates and one invalid placeholder, which is omitted. The output is **not** a live price feed.

## Keep price history and review candidates

Candidate JSON remains separate from published deal data. Import it into persistent SQLite using:

```bash
python -m scraper.history --db ./scraper/data/prices.sqlite import --input /tmp/deal-candidates.json
```

Observations are idempotent for the same source-generated timestamp. Editorial decisions persist even when a candidate reappears. Approvals are explicit; to approve a known `candidateId` after independent verification:

```bash
python -m scraper.history --db ./scraper/data/prices.sqlite review --candidate-id REPLACE_ID --status approved
```

To run a **network-disabled fixture-only Docker Compose demo** and keep SQLite data in `scraper/data`:

```bash
docker compose -f scraper/compose.yaml --profile scraper run --build --rm deal-collector
```

This does not make a deal live on any storefront. The image is not yet tested by CI, and live retailer scheduling remains planned work.

## Historical price insights (read-only)

After collecting multiple snapshots, inspect the lowest previously **observed** price for each candidate:

```bash
python -m scraper.insights --db ./scraper/data/prices.sqlite --output ./scraper/data/insights.json
```

The report marks a new observed low only after at least two distinct timestamped observations. It never treats a retailer's crossed-out regular price as proof of savings. `claimVerified` remains `false`: price-history comparisons alone cannot establish an independently verified promotional claim. Reports never publish or approve candidates.

## Live HTTP (opt-in, only authorized sources)

```bash
python -m pip install -r scraper/requirements.txt
python -m scraper.collector --config /path/to/approved-sources.json --output /tmp/candidates.json --allow-live
```

The config is a `{"sources": [...]}` object. Start from `examples/fixture-source.json`. For each approved retailer use `mode: "http"`, an HTTPS `listingUrl`, an exact `allowedDomains` list, and site/merchant/selector configuration. Extraction CSS selectors use Scrapling's `::text` and `::attr(href)` syntax. Only the listing page is fetched per source; the collector does not follow product links.

The implementation checks robots.txt (denies if unreadable except a 404), blocks unauthorized hosts, credentials in URLs, non-HTTPS and private IP literals, disables redirects, and requires `--allow-live`. There are no stealth bypasses, proxy rotations, or CAPTCHA solving. Run a single source at a time with a reasonable external schedule. Do not configure sources contrary to site terms or access permissions. Prefer official merchant/affiliate APIs, especially for Amazon.

**Current limitations:** HTTP-only (no JS browser yet), one listing page per source, no scheduler or automated publication, no DNS-level SSRF guarantee or advanced network isolation. Use network egress restrictions in production. A product's displayed crossed-out price is **not proof of a real discount**. Do not publish a savings claim without price history or independent verification.

Scrapling is a third-party BSD-3-Clause project; maintain attribution and license notices if redistributing its code.

See [the ingestion roadmap](https://github.com/drakeg/deal_monitoring_system/issues/38).
