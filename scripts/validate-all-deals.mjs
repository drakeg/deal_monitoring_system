import fs from 'node:fs';

const sites = ['adventures', 'personal-training', 'solutions'];
const required = ['id', 'category', 'title', 'merchant', 'price', 'affiliateUrl', 'imageUrl', 'whyItMatters', 'dealScore', 'status'];
let failures = 0;

for (const site of sites) {
  const path = `sites/${site}/src/data/deals.json`;
  const deals = JSON.parse(fs.readFileSync(path, 'utf8'));
  const ids = new Set();

  deals.forEach((deal, index) => {
    for (const key of required) {
      if (!(key in deal)) {
        console.error(`${path}: deal ${index} missing ${key}`);
        failures++;
      }
    }
    if (ids.has(deal.id)) {
      console.error(`${path}: duplicate deal id ${deal.id}`);
      failures++;
    }
    ids.add(deal.id);
  });

  console.log(`${path}: ${deals.length} deals validated`);
}

if (failures > 0) process.exit(1);
