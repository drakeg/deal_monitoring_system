# Mad Mallard Deals

A static, low-cost deal hub for the Mad Mallard brands:

- **Mad Mallards Adventures** — RV, camping, towing, solar, creator gear
- **Mad Mallard Personal Training** — fitness, recovery, home gym, meal prep
- **Mad Mallard Solutions** — tech, home office, cloud/dev, creator workflow gear

This MVP is intentionally static so it can be hosted cheaply on AWS using S3 + CloudFront.

## Tech Stack

- Astro static site
- JSON deal data
- S3/CloudFront-ready build output
- GitHub Actions build check

## Local Setup

```bash
npm install
npm run dev
```

Open the local URL shown by Astro.

## Build

```bash
npm run lint:data
npm run build
```

The static site is generated in `dist/`.

## Adding Deals

Edit `src/data/deals.json`.

Required fields:

- `id` — URL-safe unique ID
- `brand` — one or more of `adventures`, `personal-training`, `solutions`
- `category`
- `title`
- `merchant`
- `affiliateUrl`
- `whyItMatters`
- `dealScore` — 0-100
- `status` — `draft`, `approved`, `posted`, or `expired`

Only `approved` deals appear publicly.

## Affiliate Disclosure

The site includes a disclosure component on all main deal pages. Keep disclosures visible and accurate anywhere affiliate links appear.

## AWS Hosting Plan

Initial low-cost hosting target:

1. Build static site with `npm run build`
2. Upload `dist/` to S3
3. Serve through CloudFront
4. Use Route 53 for DNS if desired

Avoid EC2, RDS, and always-on containers for the MVP.

## Future Enhancements

- Admin UI for approving deals
- DynamoDB backend
- Lambda/EventBridge scheduled price checks
- n8n workflow for social post drafts
- Amazon Creators API integration when eligible
- Newsletter/email digest
