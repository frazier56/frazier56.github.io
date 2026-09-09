import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const file = resolve(import.meta.dirname, '..', 'apps', 'index.html');
const source = await readFile(file, 'utf8');
const names = [
  ['OneScore', 'https://app.oneworldlabs.ai/onescore', 'A verified professional credibility score you can carry across One World.'],
  ['OneJob', 'https://app.oneworldlabs.ai/jobs', 'Find work, use clear agreements and keep payment records in one place.'],
  ['OneHome', 'https://app.oneworldlabs.ai/home', 'Rent or buy with structured listings, records and agreements.'],
  ['OneEvent', 'https://app.oneworldlabs.ai/events', 'Create events, manage tickets and check guests in.'],
  ['OneSocial', 'https://app.oneworldlabs.ai/social', 'Connect professional platforms and build one verifiable identity.'],
  ['OneAgent', 'https://app.oneworldlabs.ai/agent', 'Manage opportunities, relationships and work from one agent workspace.'],
  ['OnePay', 'https://app.oneworldlabs.ai/pay', 'Run sales, receipts, refunds and closeout; card tap activates after certified-provider approval.'],
  ['One Business', 'https://app.oneworldlabs.ai/business', 'See every One World service, lead and result for your business in one account.'],
];
const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://www.oneworldlabs.ai/' },
        { '@type': 'ListItem', position: 2, name: 'Apps', item: 'https://www.oneworldlabs.ai/apps/' },
      ],
    },
    {
      '@type': 'ItemList',
      name: 'One World Platform apps',
      numberOfItems: 8,
      itemListElement: names.map(([name, url, description], index) => ({
        '@type': 'ListItem',
        position: index + 1,
        item: {
          '@type': 'SoftwareApplication',
          name,
          applicationCategory: 'BusinessApplication',
          operatingSystem: 'Web',
          url,
          publisher: { '@id': 'https://www.oneworldlabs.ai/#org' },
          description,
        },
      })),
    },
  ],
};
const replacement = `<script type="application/ld+json">\n${JSON.stringify(jsonLd)}\n</script>`;
const updated = source.replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/, replacement);
if (updated === source) throw new Error('Apps JSON-LD block was not updated.');
await writeFile(file, updated, 'utf8');
console.log('Apps JSON-LD updated to eight live app entries.');
