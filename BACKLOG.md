# Backlog

- P0: Secure first-run administrator setup and login.
- P0: Campaign management with retailer, category, event, dates and minimum discount.
- P0: Verify authorized retailer data sources; fixture tests do not establish live access.
- P0: Discovery and ranked deal feed.
- P1: Scheduling, historical prices, notifications.
- P1: Free hosting feasibility and production security.
- P2: Cross-retailer matching, affiliate reports, optional AI.

- P0: Connect approved retailer adapters to campaign scans, with provenance and persistent observations. Offline demo must remain separate from real deals.

- P0: Add operator-approved live category source configuration and safe fetching; HTML export import is an interim offline path, not live discovery.

- Live category collection: exact URL allowlist via APPROVED_CATEGORY_URLS (space-separated, default disabled), direct HTTPS without redirects, bounded HTML, existing campaign importer. CI and live authorization verification pending.

- Compose configuration: pass the operator-approved category URL allowlist to the web service, disabled by default. Live retailer validation and scheduled collection remain pending.
