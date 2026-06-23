# Contributing

## Add a deal

Edit the matching site data file:

```text
sites/adventures/src/data/deals.json
sites/personal-training/src/data/deals.json
sites/solutions/src/data/deals.json
```

Run checks before committing:

```bash
npm run lint:data
npm run check
npm run build
```

Do not commit `.terraform/`, Terraform state, `dist/`, `.astro/`, `node_modules/`, archives, or private `.tfvars` files.
