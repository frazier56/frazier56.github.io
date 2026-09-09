import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = path.resolve(import.meta.dirname, '..');
const onevoice = path.join(root, 'onevoice');
const failures = [];
const check = (condition, message) => { if (!condition) failures.push(message); };

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : (entry.name.endsWith('.html') ? [full] : []);
  });
}

function visibleAndStructuredSource(source) {
  return source
    .replace(/<script>window\.OV_DICT=[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script(?![^>]*application\/ld\+json)[\s\S]*?<\/script>/gi, '');
}

const htmlFiles = walk(onevoice);
const forbidden = /\b(?:free\s+trial|7[- ]day|seven days|plan is free|free for a week)\b|\$349|\$649|\$1,497|Enterprise starts/gi;

for (const file of htmlFiles) {
  const source = fs.readFileSync(file, 'utf8');
  const customerSource = visibleAndStructuredSource(source);
  const hits = [...customerSource.matchAll(forbidden)].map((match) => match[0]);
  check(hits.length === 0, `${path.relative(root, file)} retains retired customer copy: ${hits.join(', ')}`);

  for (const match of source.matchAll(/<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)) {
    try { JSON.parse(match[1]); }
    catch (error) { failures.push(`${path.relative(root, file)} has invalid JSON-LD: ${error.message}`); }
  }

  let scriptNumber = 0;
  for (const match of source.matchAll(/<script(?![^>]*type=["']application\/ld\+json["'])[^>]*>([\s\S]*?)<\/script>/gi)) {
    scriptNumber += 1;
    if (!match[1].trim()) continue;
    try { new vm.Script(match[1], { filename: `${file}#script${scriptNumber}` }); }
    catch (error) { failures.push(`${path.relative(root, file)} has invalid inline JavaScript: ${error.message}`); }
  }
}

const pricing = fs.readFileSync(path.join(onevoice, 'pricing', 'index.html'), 'utf8');
check(pricing.includes('data-mo="149">$149'), 'Pricing page is missing Answer at $149.');
check(pricing.includes('data-mo="297">$297'), 'Pricing page is missing Front Desk at $297.');
check(pricing.includes('$449/mo minimum'), 'Pricing page is missing the Custom $449 floor.');
check(!pricing.includes('id="paneENT"'), 'Pricing page still publishes the retired Enterprise pane.');
check(!pricing.includes('data-mo="649"'), 'Pricing page still publishes the retired Pro price.');

const checkout = fs.readFileSync(path.join(onevoice, 'get-started', 'index.html'), 'utf8');
check(checkout.includes('data-tier="starter"') && checkout.includes('data-usd="14900"'), 'Checkout is missing Answer pricing.');
check(checkout.includes('data-tier="business"') && checkout.includes('data-usd="29700"'), 'Checkout is missing Front Desk pricing.');
check(!checkout.includes('data-tier="pro2"'), 'Checkout still exposes Pro as self-serve.');
check(checkout.includes("var PRICE={ starter:{base:149,name:'Answer'}, business:{base:297,name:'Front Desk'} }"), 'Checkout calculation table is not on v8 pricing.');
check(!/founder100|founder50/i.test(checkout), 'Checkout still accepts a retired founder promo code.');
check(checkout.includes('co_fine_selfserve'), 'Checkout is missing the day-one guarantee disclosure.');

const terms = fs.readFileSync(path.join(onevoice, 'privacy', 'index.html'), 'utf8');
check(terms.includes('30 calendar days of the initial charge date'), 'Terms do not define the guarantee start date.');
check(terms.includes('support.onevoice@onesocial.ai'), 'Terms do not define the cancellation method.');
check(terms.includes('Minutes used beyond your plan allowance') && terms.includes('are not refunded'), 'Terms are missing the overage carve-out.');

const override = fs.readFileSync(path.join(onevoice, 'pricing-v8-copy.js'), 'utf8');
check(override.includes('30-day money-back guarantee'), 'Canonical pricing copy module is missing the guarantee.');
check(override.includes("copy('Front Desk'"), 'Canonical pricing copy module is missing Front Desk.');
check(override.includes('$449/mo minimum'), 'Canonical pricing copy module is missing the Custom floor.');


// The Front Desk card must agree with checkout's one-included-local-number rule.
const frontDeskFallback = pricing.match(/data-i18n="kc600c5716f">([^<]+)</)?.[1] || '';
check(/^One number, 500 minutes,/.test(frontDeskFallback), 'Front Desk fallback must promise one included number with 500 minutes.');
check(!/Two numbers, 500 minutes/i.test(visibleAndStructuredSource(pricing)), 'Front Desk customer copy must not promise two included numbers.');
check(/Every plan includes\s+one phone number/.test(visibleAndStructuredSource(pricing).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ')), 'Pricing must retain its one-included-number disclosure.');
check(checkout.includes('Every plan includes one local number'), 'Checkout must retain its one-included-local-number disclosure.');
const numberCopyContext = { window: { OV_DICT: { kc600c5716f: {} } } };
vm.runInNewContext(override, numberCopyContext);
const singleNumberPrefixes = { us: /^One number,/, es: /^Un número,/, co: /^Un número,/, de: /^Eine Nummer,/, ru: /^Один номер,/, cn: /^一个号码、/, br: /^Um número,/ };
for (const [locale, prefix] of Object.entries(singleNumberPrefixes)) {
  const text = numberCopyContext.window.OV_DICT.kc600c5716f[locale] || '';
  check(prefix.test(text) && /500/.test(text), 'Front Desk translated entitlement disagrees with one number / 500 minutes: ' + locale);
}

const dictPages = htmlFiles.filter((file) => fs.readFileSync(file, 'utf8').includes('window.OV_DICT='));
for (const file of dictPages) {
  const source = fs.readFileSync(file, 'utf8');
  check(source.includes('/onevoice/pricing-v8-copy.js'), `${path.relative(root, file)} does not load canonical pricing copy.`);
}

if (failures.length) {
  console.error(`OneVoice pricing v8 verification failed (${failures.length}):`);
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`OneVoice pricing v8 verified across ${htmlFiles.length} pages (${dictPages.length} localized pages).`);
