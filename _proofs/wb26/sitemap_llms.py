#!/usr/bin/env python3
"""Website v2 (13 Nov 2026): sitemap and llms.txt entries for the new and rebuilt pages. Idempotent."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = "https://www.oneworldlabs.ai"
TODAY = "2026-11-13"
CHANGED = ["/", "/es/", "/blog/", "/es/blog/"] + ["/apps/%s/" % k for k in ("onehome", "onejob", "oneevent", "oneride", "onepay", "onebusiness")] + \
          ["/es/apps/%s/" % k for k in ("onehome", "onejob", "oneevent", "oneride", "onepay", "onebusiness")]
p = os.path.join(ROOT, "sitemap.xml"); s = open(p).read()
for path in CHANGED:
    loc = S + path
    pr = "1.0" if path in ("/", ) else "0.9" if path in ("/es/", "/blog/") else "0.8"
    row = '  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>%s</priority></url>' % (loc, TODAY, pr)
    m = re.search(r'  <url><loc>%s</loc>.*?</url>' % re.escape(loc), s)
    if m:
        s = s.replace(m.group(0), re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>%s</lastmod>" % TODAY, m.group(0)))
    else:
        s = s.replace("</urlset>", row + "\n</urlset>")
note = "<!-- Website v2, 13 Nov 2026: new homepage, two-sided app pages (adds /apps/oneride/ and /es/apps/oneride/, /es/apps/onepay/), blog index with topic filters (adds /es/blog/). -->"
if note not in s:
    s = s.replace('<urlset ', note + "\n<urlset ", 1)
open(p, "w").write(s)
p = os.path.join(ROOT, "llms.txt"); s = open(p).read()
s = s.replace("- [OneRide](https://app.oneworldlabs.ai/rides/): book a ride, or offer rides as a driver.", "- [OneRide](https://www.oneworldlabs.ai/apps/oneride/): book a ride, or offer rides as a driver.")
s = s.replace("See https://app.oneworldlabs.ai/rides/", "See https://www.oneworldlabs.ai/apps/oneride/")
s = s.replace("- Sitio en español: https://www.oneworldlabs.ai/es/ — apps: /es/apps/onejob/, /es/apps/oneevent/, /es/apps/onehome/; agencia: /es/services/",
              "- Sitio en español: https://www.oneworldlabs.ai/es/ — apps: /es/apps/onejob/, /es/apps/oneevent/, /es/apps/onehome/, /es/apps/oneride/, /es/apps/onepay/, /es/apps/onebusiness/; guías: /es/blog/; agencia: /es/services/")
s = s.replace("- [Blog](https://www.oneworldlabs.ai/blog/)\n", "- [Blog](https://www.oneworldlabs.ai/blog/) — every guide, filterable by topic (small business, hiring in Medellín, getting hired, events, homes, rides), e.g. https://www.oneworldlabs.ai/blog/?topic=hire\n")
open(p, "w").write(s)
print("sitemap urls:", s and open(os.path.join(ROOT, "sitemap.xml")).read().count("<url>"))
