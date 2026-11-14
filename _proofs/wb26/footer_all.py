#!/usr/bin/env python3
"""Pass 5: put the shared four-column footer on every legacy page that uses the site stylesheet,
and bump the stylesheet/theme-script cache keys. Pages with their own design (OneVoice, OnePage,
OneApp, the founder card, child safety, delete account, 404) keep their own footer. Idempotent."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_v2 as B
ROOT = B.ROOT
done = skipped = 0
for dp, dn, fn in os.walk(ROOT):
    if "node_modules" in dp or "/.git" in dp or "/_proofs" in dp:
        continue
    for f in fn:
        if not f.endswith(".html"):
            continue
        path = os.path.join(dp, f)
        s = open(path).read()
        if "/assets/site.css" not in s or "<footer" not in s:
            continue
        lg = "es" if re.search(r'<html[^>]*lang="es', s) else "en"
        new = re.sub(r"<footer(?: class=\"ow-foot\")?>.*?</footer>", lambda m: B.site_footer(lg), s, count=1, flags=re.S)
        new = B.bust(new)
        if new != s:
            open(path, "w").write(new); done += 1
        else:
            skipped += 1
print("footer/cache updated in", done, "pages; unchanged", skipped)
