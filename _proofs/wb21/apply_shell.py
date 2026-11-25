#!/usr/bin/env python3
"""Run after build_city.py. The committed pages carry a newer header/footer/asset-version shell than
the generator writes; this puts that shell back on every generated page (taken from the committed
copy of the same page, or from a reference sibling for new pages). Usage: from repo root."""
import subprocess, sys, os
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "_proofs/wb21"))
import build_city as bc

REF = {"svc_en": "medellin/private-driver/index.html", "svc_es": "es/medellin/private-driver/index.html",
       "post_en": "blog/renting-in-medellin-guide/index.html", "post_es": "es/blog/arrendar-en-medellin-guia/index.html"}
def git_show(p):
    r = subprocess.run(["git", "show", "HEAD:" + p], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None
M1, M2 = '<meta content="width=device-width', '<main id="main">'
def shell(new, t):
    new = t[:t.index(M1)] + new[new.index(M1):]
    a, b = t.index("<body"), t.index(M2); c, d = new.index("<body"), new.index(M2)
    new = new[:c] + t[a:b] + new[d:]
    return new[:new.index("</main>")] + t[t.index("</main>"):]
paths = []
for lang in ("en", "es"):
    paths.append((bc.city_path(lang), "svc_" + lang))
    paths += [(bc.city_path(lang, s["slug"]), "svc_" + lang) for s in bc.SERVICES]
    paths += [(bc.art_path(lang, a), "post_" + lang) for a in bc.ARTICLES]
    paths += [(bc.post_path(lang, b), "post_" + lang) for b in bc.POSTS]
for path, kind in paths:
    f = path.strip("/") + "/index.html"
    new = open(f, encoding="utf-8").read()
    t = git_show(f) or git_show(REF[kind])
    open(f, "w", encoding="utf-8").write(shell(new, t))
print("shell applied to", len(paths))
