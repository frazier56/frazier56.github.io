import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { glob } from 'node:fs/promises';
import vm from 'node:vm';

const root = resolve(import.meta.dirname, '..');
const read = (relative) => readFile(resolve(root, relative), 'utf8');
const home = await read('index.html');
const apps = await read('apps/index.html');
const onePay = await read('apps/onepay/index.html');
const oneAgent = await read('apps/oneagent/index.html');

for await (const relative of glob('**/*.html', { cwd: root, exclude: ['node_modules/**'] })) {
  const html = await read(relative);
  assert(!html.includes('id="lang-code"'), `${relative} still renders a language code`);
  assert(!html.includes("getElementById('lang-code')"), `${relative} still updates a language code`);
  if (html.includes('id="lang-flag"')) {
    assert(/id="lang-flag"[^>]*alt=""[^>]*aria-hidden="true"/.test(html), `${relative} language flag is not decorative`);
  }
  for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (/\bsrc=|application\/ld\+json|type=["']module["']/i.test(match[1])) continue;
    new vm.Script(match[2], { filename: `${relative}:inline-script` });
  }
}

for (const product of ['OneScore', 'OneJob', 'OneHome', 'OneEvent', 'OneSocial', 'OneAgent', 'OnePay', 'One Business']) {
  assert(apps.includes(product), `Apps page is missing ${product}`);
}

const jsonMatch = apps.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
assert(jsonMatch, 'Apps page JSON-LD is missing');
const graph = JSON.parse(jsonMatch[1])['@graph'];
const itemList = graph.find((entry) => entry['@type'] === 'ItemList');
assert.equal(itemList.numberOfItems, 8, 'Apps JSON-LD count is not eight');
assert.equal(itemList.itemListElement.length, 8, 'Apps JSON-LD does not list eight apps');

assert(home.includes('href="/apps/onepay/"'), 'Homepage has no OnePay marketing link');
assert(home.includes('href="https://app.oneworldlabs.ai/pay"'), 'Homepage has no live OnePay app link');
assert(onePay.includes('>Open OnePay</a>'), 'OnePay marketing page lacks a live app CTA');
assert(onePay.includes('Card tap after provider approval'), 'OnePay marketing page lacks the provider-approval boundary');
assert(!oneAgent.includes('OneAgent<span') && !oneAgent.includes('Still being built'), 'OneAgent still appears as coming soon');

console.log('OnePay public launch checks passed: inline JavaScript, eight-app discovery, truthful provider boundary, live CTAs, and flag-only locale controls.');
