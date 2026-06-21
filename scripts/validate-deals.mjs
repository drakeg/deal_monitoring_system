import fs from 'node:fs';

const file = new URL('../src/data/deals.json', import.meta.url);
const deals = JSON.parse(fs.readFileSync(file, 'utf8'));
const ids = new Set();
const required = ['id', 'brand', 'category', 'title', 'merchant', 'affiliateUrl', 'whyItMatters', 'dealScore', 'status'];
const allowedBrands = new Set(['adventures', 'personal-training', 'solutions']);
const allowedStatuses = new Set(['draft', 'approved', 'posted', 'expired']);

let failures = 0;

for (const deal of deals) {
  for (const field of required) {
    if (deal[field] === undefined || deal[field] === null || deal[field] === '') {
      console.error(`Deal ${deal.id ?? '(missing id)'} is missing required field: ${field}`);
      failures++;
    }
  }

  if (ids.has(deal.id)) {
    console.error(`Duplicate deal id: ${deal.id}`);
    failures++;
  }
  ids.add(deal.id);

  if (!Array.isArray(deal.brand) || deal.brand.some((brand) => !allowedBrands.has(brand))) {
    console.error(`Deal ${deal.id} has invalid brand list.`);
    failures++;
  }

  if (!allowedStatuses.has(deal.status)) {
    console.error(`Deal ${deal.id} has invalid status: ${deal.status}`);
    failures++;
  }

  if (typeof deal.dealScore !== 'number' || deal.dealScore < 0 || deal.dealScore > 100) {
    console.error(`Deal ${deal.id} has invalid dealScore: ${deal.dealScore}`);
    failures++;
  }
}

if (failures > 0) {
  console.error(`Deal validation failed with ${failures} issue(s).`);
  process.exit(1);
}

console.log(`Validated ${deals.length} deals.`);
