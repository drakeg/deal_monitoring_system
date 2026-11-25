# Deal Monitoring System

[![Django monitor CI](https://github.com/drakeg/deal_monitoring_system/actions/workflows/monitor.yml/badge.svg)](https://github.com/drakeg/deal_monitoring_system/actions/workflows/monitor.yml) [![Scrapling CI](https://github.com/drakeg/deal_monitoring_system/actions/workflows/scraper.yml/badge.svg)](https://github.com/drakeg/deal_monitoring_system/actions/workflows/scraper.yml)
[![License](https://img.shields.io/github/license/drakeg/deal_monitoring_system)](https://github.com/drakeg/deal_monitoring_system/blob/main/LICENSE)

Transitioning to one unified deal alert application. See [local Docker setup](monitor/README.md). The following Astro sites are legacy and retained during migration.

## Sites

- `sites/adventures` — Mad Mallards Adventures deals
- `sites/personal-training` — Mad Mallard Personal Training deals
- `sites/solutions` — Mad Mallard Solutions deals

Each site has its own Astro app, deal data, branding, build output, and AWS deployment.

## Local setup

```bash
npm install
npm run check
npm run build
```

Run one site locally:

```bash
npm run dev:adventures
npm run dev:personal-training
npm run dev:solutions
```

## Automated ingestion (experimental)

The Scrapling-based candidate collector is in [`scraper/`](scraper/README.md). It supports offline fixture testing and strictly opt-in, robots-aware retailer HTTP collection. It **does not** publish or overwrite approved deals. See [ingestion roadmap #38](https://github.com/drakeg/deal_monitoring_system/issues/38).

## Deal data

Each site owns its data at:

```text
sites/<site>/src/data/deals.json
```

## Terraform

Each company has an independent Terraform environment:

```text
infra/terraform/environments/adventures
infra/terraform/environments/personal-training
infra/terraform/environments/solutions
```

Example:

```bash
cd infra/terraform/environments/adventures
terraform init
terraform plan
terraform apply
```

Then deploy that site's built files to the bucket shown in Terraform outputs.

## Amazon affiliate compliance

Keep affiliate disclosures visible on all deal pages. Replace placeholder links and ASINs before publishing.
