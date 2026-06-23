# Deal Monitoring System

Three separate static deal sites for the Mad Mallard companies.

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
