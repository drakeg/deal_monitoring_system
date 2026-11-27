# Rapid holiday delivery

1. Campaign CRUD and owner isolation (current).
2. Authorized retailer feeds and fixture-backed discovery.
3. Filterable deal feed and manual scan.
4. Scheduled scans, deduplication and price history.
5. Notifications and deployment hardening.

Each sprint requires tests and local Compose smoke checks. Preserve database volumes. Free hosting first; no paid resources without approval.

- Campaign deal feed implemented. Offline Scrapling UI scan submitted for CI; live source integration remains next.

- Authorized category HTML export import: bounded parsing, owner isolation, deduplicated persistent deals; CI pending. Live retailer fetching remains outstanding.

- Live category collection: exact URL allowlist via APPROVED_CATEGORY_URLS (space-separated, default disabled), direct HTTPS without redirects, bounded HTML, existing campaign importer. CI and live authorization verification pending.

- Compose configuration: pass the operator-approved category URL allowlist to the web service, disabled by default. Live retailer validation and scheduled collection remain pending.

### Repeat category collection
Successful authorized live imports save the campaign URL and selectors. Run `python manage.py collect_categories` from the monitor application environment to collect active campaigns once. The exact URL allowlist is checked again on every fetch. Run only one instance at a time, at a frequency permitted by the retailer. Automatic scheduling, source removal controls and live retailer validation remain pending.
