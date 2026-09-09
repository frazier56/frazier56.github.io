import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { glob } from 'node:fs/promises';

const root = resolve(import.meta.dirname, '..');
let changed = 0;

for await (const relative of glob('**/*.html', { cwd: root, exclude: ['node_modules/**'] })) {
  const file = resolve(root, relative);
  const before = await readFile(file, 'utf8');
  let after = before
    .replace(/<img id="lang-flag"([^>]*?) alt="[^"]+"([^>]*?)>/g, '<img id="lang-flag"$1 alt="" aria-hidden="true"$2>')
    .replace(/(?: aria-hidden="true"){2,}/g, ' aria-hidden="true"')
    .replace(/^\s*<span id="lang-code"[^>]*>[^<]*<\/span>\r?\n/gm, '')
    .replace(/^\s*document\.getElementById\('lang-code'\)\.textContent = I18N_META\[lang\]\.code;\r?\n/gm, '')
    .replace(/^\s*document\.getElementById\('lang-flag'\)\.alt = I18N_META\[lang\]\.code;\r?\n/gm, '');

  const catalogCopy = new Map([
    ['See all six apps', 'See all eight apps'],
    ['all six apps', 'all eight apps'],
    ['Ver las seis apps', 'Ver las ocho apps'],
    ['Alle sechs Apps ansehen', 'Alle acht Apps ansehen'],
    ['Все шесть приложений', 'Все восемь приложений'],
    ['查看全部六款应用', '查看全部八款应用'],
    ['Ver os seis apps', 'Ver os oito apps'],
  ]);
  for (const [oldCopy, newCopy] of catalogCopy) after = after.replaceAll(oldCopy, newCopy);

  after = after
    .replaceAll(
      '<li><span class="text-muted-foreground"><span class="font-bold">One</span>Agent · <span data-i18n="coming_soon">Coming soon</span></span></li>',
      '<li><a href="https://app.oneworldlabs.ai/agent" class="text-foreground hover:text-primary transition-colors"><span class="text-primary font-bold">One</span>Agent</a></li>\n                        <li><a href="https://app.oneworldlabs.ai/pay" class="text-foreground hover:text-primary transition-colors"><span class="text-primary font-bold">One</span>Pay</a></li>\n                        <li><a href="https://app.oneworldlabs.ai/business" class="text-foreground hover:text-primary transition-colors"><span class="text-primary font-bold">One</span> Business</a></li>',
    )
    .replaceAll(
      '<span class="menu-navitem opacity-70 cursor-default"><span><span class="menu-one">One</span>Agent</span><span class="menu-soon" data-i18n="coming_soon">Coming soon</span></span>',
      '<a href="https://app.oneworldlabs.ai/agent" class="menu-navitem"><span><span class="menu-one">One</span>Agent</span></a>\n                    <a href="https://app.oneworldlabs.ai/pay" class="menu-navitem"><span><span class="menu-one">One</span>Pay</span></a>\n                    <a href="https://app.oneworldlabs.ai/business" class="menu-navitem"><span><span class="menu-one">One</span> Business</span></a>',
    );

  if (after !== before) {
    // The marketing HTML blobs are stored with LF in Git; normalize only files this rollout edits.
    after = after.replaceAll('\r\n', '\n').replaceAll('\r', '\n');
    await writeFile(file, after, 'utf8');
    changed += 1;
  }
}

console.log(`Flag-only language picker enforced in ${changed} HTML file(s).`);
