#!/usr/bin/env python3
"""Pass 9 (Lee, 13 Nov 2026): "if it's in Russian, everything is in Russian".

English pages are translated in the browser for de / ru / zh / pt (and co / es on pages that
have no Spanish twin). The old engine only knew the blocks stamped with data-i18n, so most of
the v2 pages stayed English. This builds a STRING dictionary per language, keyed by the exact
English text (whitespace collapsed), which ow-site.js applies to every text node, alt,
aria-label, title, placeholder, <title> and meta description.

Sources, in order of trust:
  1. i18n_overrides.py   hand-checked wording (nav, buttons, headings)
  2. co / es only: the generator's own Spanish twin pages, aligned string by string (usted)
  3. machine translation (Google), cached in i18n_cache.json so rebuilds are stable
Writes assets/i18n/str-<lang>.json.   python3 _proofs/wb26/i18n_strings.py
"""
import glob, json, os, re, sys, time, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from i18n_extract import strings
from i18n_overrides import OVR
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(HERE, "i18n_cache.json")
LANGS = {"co": "es", "es": "es", "pt": "pt", "de": "de", "ru": "ru", "zh": "zh-CN"}
SKIP_DIRS = ("_proofs", "es/", "node_modules", "onevoice", "onejob", "onescore-preview", "command-center", "route", "embed")
EXTRA = os.path.join(HERE, "i18n_runtime_strings.txt")   # strings only scripts put on the page


def pages():
    for f in sorted(glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True)):
        rel = os.path.relpath(f, ROOT)
        if rel.startswith(SKIP_DIRS):
            continue
        s = open(f, errors="ignore").read()
        if "ow-site.js" in s:
            yield rel, s


def aligned_spanish():
    pairs = {}
    for rel, s in pages():
        m = re.search(r'hreflang="es" href="https://www\.oneworldlabs\.ai(/es/[^"]*)"', s)
        if not m:
            continue
        es = os.path.join(ROOT, m.group(1).lstrip("/"), "index.html")
        if not os.path.isfile(es):
            continue
        a, b = strings(s), strings(open(es).read())
        if len(a) != len(b):
            continue
        for x, y in zip(a, b):
            if x != y and x not in pairs:
                pairs[x] = y
    return pairs


# Brand names go to the translator as __n__ placeholders, which it leaves exactly as they are.
BRANDS = ["One World", "One ID", "VAIA"] + ["One" + x for x in "Event Home Job Ride Pay Business Score Agent Social Voice Page App View".split()]
BRAND_RE = re.compile("|".join(sorted(map(re.escape, BRANDS), key=len, reverse=True)))


def protect(s):
    return BRAND_RE.sub(lambda m: "__%d__" % BRANDS.index(m.group(0)), s)


def unprotect(s):
    return re.sub(r"__ ?(\d+) ?__", lambda m: BRANDS[int(m.group(1))] if int(m.group(1)) < len(BRANDS) else m.group(0), s)


def gtx(text, tl):
    data = urllib.parse.urlencode({"q": text}).encode()
    u = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=%s&dt=t" % tl
    for attempt in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, data=data, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
            return "".join(x[0] for x in r[0] if x[0])
        except Exception as e:
            time.sleep(2 + attempt * 3)
    raise RuntimeError("translate failed")


def translate(items, tl):
    out, batch, size = {}, [], 0
    def flush():
        nonlocal batch, size
        if not batch:
            return
        res = gtx("\n".join(protect(x) for x in batch), tl).split("\n")
        if len(res) == len(batch):
            for x, y in zip(batch, res):
                out[x] = unprotect(y.strip())
        else:
            for x in batch:
                out[x] = unprotect(gtx(protect(x), tl).strip())
        batch, size = [], 0
        time.sleep(0.4)
    for x in items:
        if size + len(x) > 3500:
            flush()
        batch.append(x); size += len(x) + 1
    flush()
    return out


def main():
    allstr = set()
    for rel, s in pages():
        allstr.update(strings(s))
    if os.path.isfile(EXTRA):
        allstr.update(l.strip() for l in open(EXTRA) if l.strip() and not l.startswith("#"))
    allstr = sorted(allstr)
    cache = json.load(open(CACHE)) if os.path.isfile(CACHE) else {}
    spanish = aligned_spanish()
    print("strings", len(allstr), "aligned spanish pairs", len(spanish))
    names = re.compile(r"VAIA|One World|One ID|One(?:Event|Home|Job|Ride|Pay|Business|Score|Agent|Social|Voice|Page|App|View)")
    for lg, tl in LANGS.items():
        c = cache.setdefault(tl, {})
        bad = [x for x in allstr if x in c and any(n not in c[x] for n in names.findall(x))]
        if bad:
            print(lg, "re-translating", len(bad), "with brand names protected")
            c.update(translate(bad, tl))
            json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=0, sort_keys=True)
        todo = [x for x in allstr if x not in c and not (tl == "es" and x in spanish)]
        if todo:
            print(lg, "machine-translating", len(todo))
            c.update(translate(todo, tl))
            json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=0, sort_keys=True)
        d = {}
        for x in allstr:
            y = OVR.get(lg, {}).get(x) or (spanish.get(x) if tl == "es" else None) or c.get(x)
            if y and y != x:
                d[x] = y
        p = os.path.join(ROOT, "assets/i18n/str-%s.json" % lg)
        json.dump(d, open(p, "w"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        print(lg, len(d), "entries", os.path.getsize(p) // 1024, "KB")


if __name__ == "__main__":
    main()
