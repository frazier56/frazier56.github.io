#!/usr/bin/env python3
"""Pass 3 (13 Nov 2026): sitemap and llms.txt for the feature pages, apps index, OneScore/OneAgent pages,
the OneSocial move and the blog topic hubs. Idempotent."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = "https://www.oneworldlabs.ai"; TODAY = "2026-11-13"
FEATS = ["one-profile", "payments", "messaging-and-reviews", "onesocial"]
TOPICS = ["business", "hire", "work", "events", "homes", "rides", "payments"]
paths = ["/apps/", "/apps/onescore/", "/apps/oneagent/", "/features/"] + ["/features/%s/" % f for f in FEATS] + ["/blog/topic/%s/" % t for t in TOPICS]
paths += ["/es" + p for p in paths]
p = os.path.join(ROOT, "sitemap.xml"); s = open(p).read()
for gone in ("/apps/onesocial/", "/es/apps/onesocial/"):
    s = re.sub(r"  <url><loc>%s</loc>.*?</url>\n" % re.escape(S + gone), "", s)
for path in paths:
    loc = S + path
    m = re.search(r"  <url><loc>%s</loc>.*?</url>" % re.escape(loc), s)
    if m:
        s = s.replace(m.group(0), re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>%s</lastmod>" % TODAY, m.group(0)))
    else:
        pr = "0.8" if "/blog/topic/" not in path else "0.7"
        s = s.replace("</urlset>", '  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>%s</priority></url>\n</urlset>' % (loc, TODAY, pr))
note = "<!-- Website v2 pass 3, 13 Nov 2026: /features/ pages (OneSocial moved here from /apps/onesocial/, which now redirects), /apps/ index, OneScore and OneAgent pages, blog topic hubs /blog/topic/<topic>/; EN + /es/. -->"
if note not in s:
    s = s.replace("<urlset ", note + "\n<urlset ", 1)
open(p, "w").write(s)
p = os.path.join(ROOT, "llms.txt"); s = open(p).read()
s = s.replace("- [OneSocial](https://www.oneworldlabs.ai/apps/onesocial/): your professional presence and social platforms in one profile.\n", "")
block = """
## Works across every app (features, not separate apps)
- [One profile](https://www.oneworldlabs.ai/features/one-profile/): one One ID login and one profile across every One World app.
- [Payments](https://www.oneworldlabs.ai/features/payments/): card, Nequi or PSE by link or QR code through OnePay; eligible OneJob card payments held until both sides mark the job complete; One World is not a bank.
- [Messages and reviews](https://www.oneworldlabs.ai/features/messaging-and-reviews/): one inbox across apps; reviews come from jobs done in the app.
- [OneSocial](https://www.oneworldlabs.ai/features/onesocial/) (coming soon): your social profile, media and feed across One World. It is a feature, not a separate app.
- All features: https://www.oneworldlabs.ai/features/
"""
if "## Works across every app" not in s:
    s = s.replace("\n## The Agency", block + "\n## The Agency", 1)
hubs = "- Guides by topic: " + ", ".join("[%s](https://www.oneworldlabs.ai/blog/topic/%s/)" % (n, t) for t, n in [
    ("business", "small business"), ("hire", "hiring in Medellín"), ("work", "getting hired"), ("events", "events"),
    ("homes", "homes"), ("rides", "private drivers"), ("payments", "getting paid")]) + "\n"
if "- Guides by topic:" not in s:
    s = s.replace("- [Blog](https://www.oneworldlabs.ai/blog/)", hubs + "- [Blog](https://www.oneworldlabs.ai/blog/)", 1)
s = s.replace("e.g. https://www.oneworldlabs.ai/blog/?topic=hire", "e.g. https://www.oneworldlabs.ai/blog/topic/hire/")
open(p, "w").write(s)
print("ok")
