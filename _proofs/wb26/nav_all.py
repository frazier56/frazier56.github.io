#!/usr/bin/env python3
"""13 Nov 2026 (Lee): the header said "The apps" and "For business" as if they were different
things. Put the generator's header links (Apps + OneBusiness) on every page that still has the old
header, generated or not. Idempotent."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_v2 as B
done = 0
for dp, dn, fn in os.walk(B.ROOT):
    if "node_modules" in dp or "/.git" in dp or "/_proofs" in dp:
        continue
    for f in fn:
        if f.endswith(".html"):
            p = os.path.join(dp, f); s = open(p).read(); n = B.fix_nav(s)
            if n != s:
                open(p, "w").write(n); done += 1
print("header links updated in", done, "pages")
