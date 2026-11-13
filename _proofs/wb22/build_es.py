#!/usr/bin/env python3
"""WB-22 (12 Nov 2026) — Spanish pages with their own addresses.

Google only ranks words that are in the HTML it downloads. Until now Spanish existed only after
the browser swapped the English text, so no Spanish page could ever be found. This script writes
a real /es/ copy of each page below, in formal Colombian Spanish (usted), and links each pair
with hreflang.

How: the same rebuild the browser does (assets/ow-site.js, rebuild()) is run here at build time.
Strings come from _proofs/wb22/es-usted.json (the formal rewrite Lee asked for) and fall back to
assets/i18n/co.json, whose remaining strings carry no tú form. Re-run after editing an English
page:  python3 _proofs/wb22/build_es.py   (from the repo root). It also (re)writes the hreflang
links on the English pages, idempotently.
"""
import copy, html, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://www.oneworldlabs.ai"
JSV = "wb23"

# English path -> Spanish path. Only pages built on the shared data-i18n template are here.
PAGES = {
    "/": "/es/",
    "/services/": "/es/services/",
    "/apps/onejob/": "/es/apps/onejob/",
    "/apps/oneevent/": "/es/apps/oneevent/",
    "/apps/onehome/": "/es/apps/onehome/",
    "/apps/onesocial/": "/es/apps/onesocial/",
    "/apps/onescore/": "/es/apps/onescore/",
    "/apps/onebusiness/": "/es/apps/onebusiness/",
}
BLOG_ES = {"/blog/dj-cost-medellin-2026/": "/es/blog/precio-dj-medellin-2026/", "/blog/cleaner-cost-medellin-2026/": "/es/blog/precio-empleada-por-dias-medellin-2026/", "/blog/private-driver-cost-medellin-2026/": "/es/blog/precio-conductor-privado-medellin-2026/", "/blog/videographer-cost-medellin-2026/": "/es/blog/precio-videografo-medellin-2026/"}
EXTRA_LINKS = {"/#destinations": "/es/#destinations", "/#contact": "/es/#contact"}

CO = json.load(open(os.path.join(ROOT, "assets/i18n/co.json"), encoding="utf-8"))
US = json.load(open(os.path.join(ROOT, "_proofs/wb22/es-usted.json"), encoding="utf-8"))
TOK = re.compile(r"<(\d+)/>|<(\d+)>|</(\d+)>|([^<]+)")


def fpath(p):
    return os.path.join(ROOT, p.strip("/"), "index.html") if p != "/" else os.path.join(ROOT, "index.html")


def es_string(key):
    return US.get(key) or CO.get(key)


def rebuild(soup, el, tpl):
    els = el.find_all(True)                     # document order, like querySelectorAll('*')
    out, stack = [], [None]
    def add(node):
        (out.append(node) if stack[-1] is None else stack[-1].append(node))
    for m in TOK.finditer(tpl):
        if m.group(1) is not None:
            add(copy.copy(els[int(m.group(1))]))
        elif m.group(2) is not None:
            src = els[int(m.group(2))]
            c = soup.new_tag(src.name, attrs=dict(src.attrs))
            add(c); stack.append(c)
        elif m.group(3) is not None:
            if len(stack) > 1: stack.pop()
        else:
            add(NavigableString(html.unescape(m.group(4))))
    el.clear()
    for n in out:
        el.append(n)


def hreflang_block(en, es):
    return ('<link rel="alternate" hreflang="en" href="%s%s"/>'
            '<link rel="alternate" hreflang="es" href="%s%s"/>'
            '<link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, en, SITE, es, SITE, en))


def set_hreflang(s, en, es):
    s = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]*"/>', "", s)
    return re.sub(r'(<link href="[^"]+" rel="canonical"/>)', lambda m: m.group(1) + hreflang_block(en, es), s, count=1)


def bump_js(s):
    return re.sub(r'/assets/ow-site\.js\?v=[^"]+"', '/assets/ow-site.js?v=%s"' % JSV, s)


def build(en, es):
    src = open(fpath(en), encoding="utf-8").read()
    soup = BeautifulSoup(src, "html.parser")
    missing = []
    for el in soup.select("[data-i18n]"):
        k = el.get("data-i18n"); t = es_string(k)
        if not t: missing.append(k); continue
        rebuild(soup, el, t)
    for el in soup.select("[data-i18n-attr]"):
        for pair in el["data-i18n-attr"].split(";"):
            if ":" not in pair: continue
            a, k = pair.split(":", 1); t = es_string(k)
            if t: el[a] = html.unescape(t)
            else: missing.append(k)
    for el in soup.select("[data-i18n],[data-i18n-attr]"):
        el.attrs.pop("data-i18n", None); el.attrs.pop("data-i18n-attr", None)
    if missing:
        sys.exit("missing strings on %s: %s" % (en, missing))

    h = soup.html
    h["lang"] = "es-CO"; h["data-ow-static"] = "co"
    title = soup.title.get_text()
    desc = soup.find("meta", attrs={"name": "description"})["content"]
    for prop in ("og:title",):
        t = soup.find("meta", attrs={"property": prop}); t and t.__setitem__("content", title)
    for name in ("twitter:title",):
        t = soup.find("meta", attrs={"name": name}); t and t.__setitem__("content", title)
    for prop in ("og:description",):
        t = soup.find("meta", attrs={"property": prop}); t and t.__setitem__("content", desc)
    for name in ("twitter:description",):
        t = soup.find("meta", attrs={"name": name}); t and t.__setitem__("content", desc)
    t = soup.find("meta", attrs={"property": "og:url"}); t and t.__setitem__("content", SITE + es)
    soup.find("link", attrs={"rel": "canonical"})["href"] = SITE + es

    # links: every page that has a Spanish twin points at it
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href in EXTRA_LINKS: a["href"] = EXTRA_LINKS[href]
        elif href in PAGES: a["href"] = PAGES[href]
        elif href.startswith("/medellin/"): a["href"] = "/es" + href      # WB-21 city pages
        elif href in BLOG_ES: a["href"] = BLOG_ES[href]                  # WB-25 guides

    # JSON-LD on the app pages: breadcrumb in Spanish, this page's own URL, Spanish description
    for sc in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try: data = json.loads(sc.string)
        except Exception: continue
        if en == "/": continue                   # the home graph describes the company; leave it
        for node in data.get("@graph", []):
            if node.get("@type") == "BreadcrumbList":
                for it in node["itemListElement"]:
                    path = it["item"].replace(SITE, "")
                    it["item"] = SITE + PAGES.get(path, path)
                    it["name"] = {"Home": "Inicio"}.get(it["name"], it["name"])
            elif node.get("url") == SITE + en:
                node["url"] = SITE + es; node["description"] = desc; node["inLanguage"] = "es-CO"
        sc.string = json.dumps(data, ensure_ascii=False)

    out = str(soup)
    # The early language script: this page is Spanish, never hidden while a dictionary loads.
    out = re.sub(r'var l=ok\(new URLSearchParams\(location\.search\)\.get\("owl_lang"\)\)\|\|ok\(localStorage\.getItem\("owl-lang"\)\)\|\|"en";',
                 'var l="co";', out)
    out = out.replace('if(l!=="en"){document.documentElement.classList.add("ow-i18n-pending");}', "")
    out = set_hreflang(out, en, es)
    out = out.replace('<meta content="website" property="og:type"/>',
                      '<meta content="website" property="og:type"/><meta content="es_CO" property="og:locale"/><meta content="en_US" property="og:locale:alternate"/>', 1)
    out = bump_js(out)
    os.makedirs(os.path.dirname(fpath(es)), exist_ok=True)
    open(fpath(es), "w", encoding="utf-8").write(out)

    # the English twin gets the same pair
    s = open(fpath(en), encoding="utf-8").read()
    s2 = bump_js(set_hreflang(s, en, es))
    if s2 != s: open(fpath(en), "w", encoding="utf-8").write(s2)
    return fpath(es)


if __name__ == "__main__":
    for en, es in PAGES.items():
        print("wrote", os.path.relpath(build(en, es), ROOT))
