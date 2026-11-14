#!/usr/bin/env python3
"""Website v2 (13 Nov 2026, Lee's decisions): new homepage, one page per app with a two-sided toggle,
and a filterable blog index, in English and Colombian Spanish.

Reads the header, footer, head scripts and contact block from the BASE commit's index.html and
es/index.html (so the shared header stays exactly as it is) and writes:
  index.html, es/index.html
  apps/{onehome,onejob,oneevent,oneride,onepay,onebusiness}/index.html  (+ es/apps/…)
  blog/index.html, es/blog/index.html
Idempotent: run it again after editing content.py.  python3 _proofs/wb26/build_v2.py
"""
import html, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import (APP, APPS, APP_BY, ES_APP_PAGES, HOME, SCREENS, EXPLORER, STORY, HOME_GUIDES, PAGES,
                     JOB_NEEDS, NEED_NAMES, TOPICS, POST_TAGS, FALLBACK_IMG, BLOG)
from content3 import APP_PAGES3, FEATURES, FEATURE_BY, FEAT_PAGES, FEAT_INDEX, APPS_INDEX, HUBS
from content5 import FEATURED, WHY, FOOTER, DOCS, DOC_IMG, INFRA
PAGES.update(APP_PAGES3)
for _k, _n, _live, _img, _line in FEATURES:
    if _k not in APP_BY:
        APP_BY[_k] = (_k, _n["en"], "#0D9488", _live, None, _img, {"en": (_line["en"], _line["en"]), "es": (_line["es"], _line["es"])})

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "05c5c9b"          # the commit whose header/footer we keep
SITE = "https://www.oneworldlabs.ai"
V = "v2h"                  # cache-buster for v2.css / v2.js
E = lambda s: html.escape(s, quote=True)


def base(path):
    return subprocess.check_output(["git", "-C", ROOT, "show", "%s:%s" % (BASE, path)]).decode()


TPL = {"en": base("index.html"), "es": base("es/index.html")}


def cut(s, a, b, incl=True):
    i = s.index(a); j = s.index(b, i) + (len(b) if incl else 0)
    return s[i:j]


PARTS = {}
for lg, s in TPL.items():
    pre = s[:s.index("<title")]
    assert pre.rstrip().endswith('name="viewport"/>'), lg
    body_open = s[s.index("<body"):s.index("<header")]
    assert body_open.startswith("<body>"), body_open[:30]
    PARTS[lg] = dict(
        pre=pre,
        ld=re.search(r'<script type="application/ld\+json">.*?</script>', s, re.S).group(0).replace(
            "OneEvent, OneJob, OneHome, OneRide and OnePay are live; OneSocial, OneScore, OneAgent and One Business are coming soon",
            "OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore and OneAgent are live; OneSocial is coming soon"),
        body=body_open.replace("<body>", '<body class="v2">', 1),
        header=cut(s, "<header", "</header>").replace('<a href="/blog/">Blog</a>', '<a href="/es/blog/">Blog</a>') if lg == "es" else cut(s, "<header", "</header>"),
        footer=cut(s, "<footer", "</footer>").replace('<a href="/blog/">Lea el blog</a>', '<a href="/es/blog/">Lea el blog</a>') if lg == "es" else cut(s, "<footer", "</footer>"),
        contact=cut(s, '<section class="contact" id="contact">', "</section>"),
        widget=re.search(r'<script[^>]*widgets\.leadconnectorhq\.com/loader\.js[^>]*></script>', s).group(0),
        vaia=re.search(r'<script>/\* feature flag vaia.*?</script>', s, re.S).group(0),
        vaia_box=cut(s, '<div class="asleep" id="vaia-widget">', "<footer", incl=False),
    )

# Lee 13 Nov 2026: "For business" read as something other than the apps. OneBusiness is ONE of the
# apps, so the header says Apps + OneBusiness (the phone menu is built from these same links).
# Pass 7 (Lee 13 Nov 2026): the header is Apps · Infrastructure · Blog. OneBusiness is reached from
# Apps like every other app. The phone menu is built from these same links.
NAV_NEW = {
    "Main": '<nav aria-label="Main" data-i18n="kb7e4919ac" data-i18n-attr="aria-label:keb814be3c"><a href="/apps/">Apps</a><a href="/infrastructure/">Infrastructure</a><a href="/blog/">Blog</a></nav>',
    "Principal": '<nav aria-label="Principal"><a href="/es/apps/">Las apps</a><a href="/es/infrastructure/">Infraestructura</a><a href="/es/blog/">Blog</a></nav>',
}


def fix_nav(s):
    return re.sub(r'<nav aria-label="(Main|Principal)"[^>]*>.*?</nav>', lambda m: NAV_NEW[m.group(1)], s, count=1, flags=re.S)


for _lg in PARTS:
    PARTS[_lg]["header"] = fix_nav(PARTS[_lg]["header"])
    assert "/infrastructure/" in PARTS[_lg]["header"], _lg

APP_PATHS = {"/home", "/jobs", "/events", "/rides", "/pay", "/business", "/onescore", "/agent"}

# ── Spanish twins for blog posts (read from each English post's hreflang) ─────────────────────
POSTS = {"en": {}, "es": {}}
PAIR = {}   # en slug -> es slug
for lg, root in (("en", "blog"), ("es", "es/blog")):
    d = os.path.join(ROOT, root)
    for slug in sorted(os.listdir(d)):
        f = os.path.join(d, slug, "index.html")
        if not os.path.isfile(f):
            continue
        s = open(f).read()
        title = html.unescape(re.search(r"<title[^>]*>(.*?)</title>", s, re.S).group(1)).strip()
        title = re.sub(r"\s*\|\s*(One World( Blog)?|Blog de One World)\s*$", "", title)
        m = re.search(r'<meta content="([^"]*)"[^>]*name="description"', s)
        desc = html.unescape(m.group(1)) if m else ""
        m = re.search(r'"datePublished":\s*"([^"]+)"', s)
        date = m.group(1)[:10] if m else "2026-11-12"
        m = re.search(r'<img[^>]*src="(/blog/img/[^"]+)"', s)
        img = m.group(1) if m else None
        POSTS[lg][slug] = dict(slug=slug, title=title, desc=desc, date=date, img=img)
        if lg == "en":
            m = re.search(r'hreflang="es" href="https://www\.oneworldlabs\.ai/es/blog/([^/"]+)/"', s)
            if m:
                PAIR[slug] = m.group(1)
ES2EN = {v: k for k, v in PAIR.items()}
for slug, p in POSTS["es"].items():
    en = ES2EN.get(slug)
    p["en"] = en
    if not p["img"] and en:
        p["img"] = FALLBACK_IMG.get(en)
for slug, p in POSTS["en"].items():
    p["en"] = slug
    if not p["img"]:
        p["img"] = FALLBACK_IMG.get(slug, "/assets/v2/img/team.jpg")
for lg in POSTS:
    for p in POSTS[lg].values():
        p["img"] = p["img"] or "/assets/v2/img/team.jpg"


def L(lg, h):
    """Site link for a language. App paths go to the app; English-only pages stay English."""
    if h in APP_PATHS or h.startswith("/feed"):
        return APP + h
    if h.startswith("http") or lg == "en" or h.startswith("/es/"):
        return h
    if h.startswith("/#"):
        return "/es/" + h[1:]
    m = re.match(r"^/apps/([a-z]+)/(.*)$", h)
    if m and m.group(1) in ES_APP_PAGES:
        return "/es/apps/%s/%s" % (m.group(1), m.group(2))
    m = re.match(r"^/blog/([^/]+)/$", h)
    if m and m.group(1) in PAIR:
        return "/es/blog/%s/" % PAIR[m.group(1)]
    if h == "/blog/":
        return "/es/blog/"
    if h.startswith("/features/") or h == "/apps/" or h.split("?")[0] in ("/why/", "/infrastructure/", "/careers/", "/partners/", "/investors/", "/press/", "/safety/", "/accessibility/", "/cookies/", "/sms-terms/", "/legal/ip/"):
        return "/es" + h
    if h.startswith("/medellin/") or h == "/services/":
        return "/es" + h
    return h


def page_url(lg, path):
    return SITE + (path if lg == "en" else "/es" + path)


def head(lg, title, desc, path, og, ld):
    url = page_url(lg, path)
    alts = ('<link rel="alternate" hreflang="en" href="%s"/><link rel="alternate" hreflang="es" href="%s"/>'
            '<link rel="alternate" hreflang="x-default" href="%s"/>') % (SITE + path, SITE + "/es" + path, SITE + path)
    og = og if og.startswith("http") else SITE + og
    return (PARTS[lg]["pre"] +
            '<title>%s</title><meta content="%s" name="description"/><link href="%s" rel="canonical"/>%s'
            '<meta content="%s" property="og:title"/><meta content="%s" property="og:description"/><meta content="%s" property="og:url"/>'
            '<link href="/owl-manifest.webmanifest" rel="manifest"/><link href="/apple-touch-icon.png" rel="apple-touch-icon"/>'
            '<meta content="#FAFAF8" id="theme-color-meta" name="theme-color"/><meta content="website" property="og:type"/>'
            '<meta content="One World Labs" property="og:site_name"/><meta content="%s" property="og:image"/>'
            '<meta content="%s" property="og:locale"/>'
            '<meta content="summary_large_image" name="twitter:card"/><meta content="%s" name="twitter:title"/>'
            '<meta content="%s" name="twitter:description"/><meta content="%s" name="twitter:image"/>'
            '<link rel="stylesheet" href="/assets/v2/v2.css?v=%s">%s</head>\n') % (
        E(title), E(desc), url, alts, E(title), E(desc), url, og, "en_US" if lg == "en" else "es_CO",
        E(title), E(desc), og, V, ld)


def ldjson(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False)


def tail(lg, home=False):
    t = ('<script src="/assets/ow-site.js?v=wb27" defer></script>\n'
         '<script src="/assets/site-theme.js?v=09f8469a" defer></script>\n'
         '<script src="/assets/v2/v2.js?v=%s" defer></script>\n') % V
    if home:
        t += PARTS[lg]["widget"] + "\n" + PARTS[lg]["vaia"] + "\n"
    return t + "</body></html>\n"


def site_footer(lg):
    F = FOOTER[lg]
    cols = "".join('<details class="fcol" open><summary>%s</summary><ul>%s</ul></details>' % (
        E(h), "".join('<li><a href="%s">%s</a></li>' % (u, E(t)) for t, u in links)) for h, links in F["cols"])
    return ('<footer class="ow-foot"><div class="fbrand"><span class="eyebrow">%s</span><strong>One World.</strong></div>'
            '<nav class="fcols" aria-label="%s">%s</nav><div class="fbottom"><p>%s</p></div>'
            '<script>if(window.matchMedia&&matchMedia("(max-width:680px)").matches)document.querySelectorAll(".ow-foot details").forEach(function(d){d.open=false})</script></footer>') % (
        E(F["tag"]), E(F["label"]), cols, E(F["rights"]))


def doc(lg, headhtml, main, home=False):
    p = PARTS[lg]
    foot = site_footer(lg)
    return headhtml + p["body"] + p["header"] + '<main id="main">' + main + "</main>" + (p["vaia_box"] if home else "") + foot + tail(lg, home)


def bust(s):
    return s.replace("site.css?v=wb21", "site.css?v=wb26").replace("site.css?v=wb9", "site.css?v=wb26").replace("site-theme.js?v=09f8469a", "site-theme.js?v=wb26")


def write(rel, s):
    s = bust(s)
    f = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w").write(s)
    print("wrote", rel, len(s) // 1024, "KB")


PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2.5" width="12" height="19" rx="3"/><path d="M11 18.5h2"/></svg>'
LEFT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>'
RIGHT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>'
EXT = " ↗"


def mark(k):
    return "/assets/v2/marks/%s.png" % k


def img(src, alt="", cls="", lazy=True):
    return '<img src="%s" alt="%s"%s%s decoding="async"/>' % (src, E(alt), ' class="%s"' % cls if cls else "", ' loading="lazy"' if lazy else "")


def app_page(lg, k):
    if k in FEATURE_BY:
        return L(lg, "/features/%s/" % k)
    return L(lg, "/apps/%s/" % k)


def guide_cards(lg, slugs, cls="cards"):
    out = []
    for slug in slugs:
        p = POSTS[lg].get(slug)
        if not p:
            continue
        tags, app = POST_TAGS.get(p["en"] or "", ("", None))
        out.append('<a class="gcard" href="%s">%s<div><em>%s</em><h3>%s</h3><p>%s</p><time datetime="%s">%s</time></div></a>' % (
            ("/blog/%s/" if lg == "en" else "/es/blog/%s/") % slug, img(p["img"]), E(APP_BY[app][1] if app else "One World"),
            E(p["title"]), E(p["desc"]), p["date"], fmt_date(lg, p["date"])))
    return '<div class="%s n%d">%s</div>' % (cls, len(out), "".join(out))


MONTHS = {"en": "January February March April May June July August September October November December".split(),
          "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()}


def fmt_date(lg, d):
    y, m, dd = d.split("-")
    mm = MONTHS[lg][int(m) - 1]
    return "%d %s %s" % (int(dd), mm, y) if lg == "en" else "%d de %s de %s" % (int(dd), mm, y)


def open_btn(lg, k, label=None, cls="btn"):
    a = APP_BY[k]
    if not a[3]:
        return '<span class="btn soon" aria-disabled="true">%s</span>' % E(HOME[lg]["soon"])
    return '<a class="%s" href="%s">%s</a>' % (cls, APP + a[4], E(label or HOME[lg]["open_x"].format(n=a[1])))


def one_card(lg, k, first=False):
    a = APP_BY[k]
    line, title = a[6][lg]
    badge = '<span class="badge live">%s</span>' % E(HOME[lg]["live"]) if a[3] else '<span class="badge">%s</span>' % E(HOME[lg]["soon"])
    act = '<a class="link" href="%s">%s</a>' % (app_page(lg, k), E(HOME[lg]["learn"]))
    if a[3]:
        act = open_btn(lg, k) + act
    return ('<article class="oc" aria-roledescription="slide">%s<div class="oc-body"><div class="oc-id">%s<strong translate="no">%s</strong>%s</div>'
            '<h4>%s</h4><p>%s</p><div class="oc-act">%s</div></div></article>') % (
        img(a[5], "", lazy=not first), biz_icon(k), a[1], badge, E(title), E(line), act)


# Pass 8 (Lee): the phone in the centre of "Explore the apps" plays its loop; the rest stay still.
# 448x960 web cuts of the 1080p loops (assets/v2/vid/). The src is set by v2.js on first focus.
SCREEN_VIDEO = {"onebusiness", "oneevent", "onehome", "onejob", "onescore"}


def screen_video(k, poster):
    if k not in SCREEN_VIDEO:
        return ""
    return '<video class="scr-vid" muted playsinline loop preload="none" poster="%s" data-src="/assets/v2/vid/%s.mp4?v=1" aria-hidden="true" tabindex="-1"></video>' % (poster, k)


# ── HOME ─────────────────────────────────────────────────────────────────────────────────────
def build_home(lg):
    H = HOME[lg]
    slides = []
    for k, src, t in SCREENS:
        a = APP_BY[k]
        title, sub, tag = t[lg]
        if a[3]:
            act = '<a class="ptag" href="%s">%s</a>' % (APP + a[4], E(tag))
        else:
            act = '<span class="ptag soon">%s</span>' % E(H["soon"])
        slides.append(
            '<div class="slide"><div class="phone" role="group" aria-label="%s" style="--hue:%s"><div class="scr">%s%s<div class="lane-bar"><i></i><span translate="no">%s</span></div>'
            '<div class="post"><strong>%s</strong><span>%s</span>%s</div></div></div>'
            '<a class="link more-link" href="%s" aria-label="%s">%s</a></div>' % (
                a[1], a[2], img(src, "", lazy=False), screen_video(k, src), a[1], E(title), E(sub), act,
                app_page(lg, k), E(H["learn_x"].format(n=a[1])), E(H["learn"])))
    hero = ('<section class="hero2"><div class="wrap"><div class="hero-copy"><h1>%s</h1><p class="hero-sub">%s</p><p class="lead">%s</p><p class="why-link"><a class="link" href="%s" aria-label="%s">%s</a></p>'
            '<div class="hero-cta"><a class="btn glass shine" href="%s/">%s%s</a></div></div></div>'
            '<div class="apps2" id="destinations"><div class="wrap"><h2 class="apps2-h">%s</h2></div>'
            '<div class="stage" data-screens data-start="0" role="region" aria-roledescription="carousel" aria-label="%s"><div class="screens">%s</div>'
            '<div class="oc-nav below"><button type="button" data-prev aria-label="%s">%s</button>'
            '<span class="oc-count" aria-live="polite">1 / %d</span><button type="button" data-next aria-label="%s">%s</button></div>'
            '<p class="see-all"><a class="link" href="%s">%s</a></p></div></div></section>') % (
        E(H["h1"]), E(H["sub"]), E(H["lead"]), L(lg, "/why/"), E(H["why_x"]), E(H["why"]), APP, PHONE, E(H["open"]),
        E(H["oc_h3"]), E(H["oc_h3"]), "".join(slides), E(H["prev"]), LEFT, len(SCREENS), E(H["next"]), RIGHT, L(lg, "/apps/"), E(H["see_all"]))

    rows = []
    for k, pic, words in FEATURED:
        a = APP_BY[k]
        h3, p = words[lg]
        rows.append('<article class="row"><div class="row-media">%s</div><div><span class="row-tag">%s<span translate="no">%s</span></span>'
                    '<h3>%s</h3><p>%s</p><div class="oc-act"><a class="btn small-btn" href="%s">%s</a><a class="link" href="%s">%s</a></div></div></article>' % (
                        img(pic, h3), biz_icon(k), a[1], E(h3), E(p), APP + a[4], E(H["open_x"].format(n=a[1])), app_page(lg, k), E(H["learn"])))
    biz = ('<section class="sec" id="business"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p></div>'
           '<div class="rows">%s</div><p class="more"><a class="btn ghost" href="%s">%s</a></p></div></section>') % (
        E(H["feat_eyebrow"]), E(H["feat_h2"]), E(H["feat_p"]), "".join(rows), L(lg, "/apps/"), E(H["feat_all"]))

    steps = "".join('<div class="step"><b>%d</b><div><h4>%s</h4><p>%s</p></div></div>' % (i + 1, E(t), E(p)) for i, (t, p) in enumerate(H["steps"]))
    oneid = ('<section class="sec sec-oneid"><div class="wrap oneid"><div class="oneid-mark">%s</div>'
             '<div><span class="eyebrow">%s</span><h2 style="font-size:clamp(32px,4vw,52px);font-weight:800;letter-spacing:-.045em;line-height:1.05">%s</h2><div class="steps3">%s</div>%s</div></div></section>') % (
        svg(ic("id")), E(H["id_eyebrow"]), E(H["id_h2"]), steps, features_row(lg, compact=True))
    gp = POSTS[lg][HOME_GUIDES[lg][0]]
    gt, gapp = POST_TAGS.get(gp["en"] or "", ("", None))
    one = ('<a class="feature-post" href="%s">%s<div><em>%s</em><h3 class="fp-h">%s</h3><p>%s</p><time datetime="%s">%s</time></div></a>') % (
        ("/blog/%s/" if lg == "en" else "/es/blog/%s/") % gp["slug"], img(gp["img"]), E(APP_BY[gapp][1] if gapp else "One World"),
        E(gp["title"]), E(gp["desc"]), gp["date"], fmt_date(lg, gp["date"]))
    guides = ('<section class="sec"><div class="wrap"><div class="oc-top"><div><span class="eyebrow">%s</span><h2 class="g-h2">%s</h2></div><a class="link" href="%s">%s</a></div>%s</div></section>') % (
        E(H["g_eyebrow"]), E(H["g_h2"]), L(lg, "/blog/"), E(H["g_all"]), one)
    contact = '<div class="wrap" style="padding-bottom:40px">' + PARTS[lg]["contact"].replace('<section class="contact" id="contact">', '<section class="contact" id="contact" style="max-width:none;margin:0;padding:0">') + "</div>"
    main = hero + biz + oneid + guides + contact
    ld = PARTS[lg]["ld"]
    h = head(lg, H["title"], H["desc"], "/", "/og-cover.png", ld)
    write("index.html" if lg == "en" else "es/index.html", doc(lg, h, main, home=True))


# OneBusiness's four tools (Lee 13 Nov 2026): one line-icon each, same stroke as the feature icons.
BIZ_ICON = {
    "voice": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "page": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5a14.5 14.5 0 0 1 0 19M12 2.5a14.5 14.5 0 0 0 0 19"/>',
    "app": '<rect x="6" y="2.5" width="12" height="19" rx="3"/><path d="M11 18.5h2"/>',
    "view": '<rect x="3" y="3" width="18" height="18" rx="3.5"/><path d="M7.5 16.5v-4M12 16.5V8M16.5 16.5v-6"/>',
}


# Pass 7 (Lee): the coloured crescent is the same mark in every colour, so outside the wordmark and
# the app-page title it is replaced by a line icon per app in the same tinted square.
APP_ICON = {
    "onebusiness": '<path d="M4 9.5 5.5 4h13L20 9.5"/><path d="M4 9.5a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0"/><path d="M5.5 11.5V20h13v-8.5"/><path d="M10 20v-4.5h4V20"/>',
    "oneevent": '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6h15A1.5 1.5 0 0 1 21 7.5V10a2 2 0 0 0 0 4v2.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 16.5V14a2 2 0 0 0 0-4z"/><path d="M14.5 6v2.5M14.5 11v2M14.5 15.5V18"/>',
    "onehome": '<path d="M3 11 12 4l9 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "onepay": '<path d="M21 3 10 14"/><path d="M21 3l-7 18-4-7-7-4z"/>',
    "onejob": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M8.5 7V5.5A1.5 1.5 0 0 1 10 4h4a1.5 1.5 0 0 1 1.5 1.5V7"/><path d="M3 12.5h18"/>',
    "oneride": '<path d="M4 16.5v-4L6.2 7h11.6l2.2 5.5v4z"/><path d="M4 12.5h16"/><circle cx="7.5" cy="16.5" r="1.8"/><circle cx="16.5" cy="16.5" r="1.8"/>',
    "onescore": '<path d="M4 17a8 8 0 1 1 16 0"/><path d="m12 17 4-5"/><circle cx="12" cy="17" r="1.3"/>',
    "oneagent": '<circle cx="9" cy="8" r="3.5"/><path d="M3 20c.8-3.6 3.2-5.5 6-5.5s5.2 1.9 6 5.5"/><path d="m18 4.5.9 1.8 2 .3-1.45 1.4.35 2-1.8-.95-1.8.95.35-2L15.1 6.6l2-.3z"/>',
    "onesocial": '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><path d="m15 17 2 2 4-4"/>',
    "id": '<rect x="3" y="5" width="18" height="14" rx="3"/><circle cx="9" cy="11" r="2.3"/><path d="M5.8 16c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4"/><path d="M14.5 10h4M14.5 13.5h3"/>',
    "contract": '<path d="M14 3H6.5A1.5 1.5 0 0 0 5 4.5v15A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5V8z"/><path d="M14 3v5h5"/><path d="M8.5 16.5c1.2 0 1.6-3 2.8-3s.4 3 1.6 3 1.2-1.5 2.6-1.5"/>',
    "sales": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "marketing": '<path d="M3 10v4h3l7 4V6l-7 4z"/><path d="M17 9a4 4 0 0 1 0 6"/>',
    "signature": '<path d="M3 16c2.5 0 3.5-9 6-9s-1 9 2 9 3-4 5-4 1.5 4 5 4"/><path d="M3 20.5h18"/>',
    "star": '<path d="m12 3.5 2.6 5.3 5.9.9-4.25 4.1 1 5.8L12 16.9l-5.25 2.7 1-5.8L3.5 9.7l5.9-.9z"/>',
}


def ic(k):
    return APP_ICON.get(k) or FICON.get(k) or BIZ_ICON.get(k)


def biz_icon(k, cls="biz-ic"):
    return '<span class="%s"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg></span>' % (cls, ic(k))


def oneview_mock(lg):
    """An illustration of the OneView dashboard: four tiles, no invented numbers."""
    names = {"en": ("Sales", "Bookings", "Payouts", "Reviews"), "es": ("Ventas", "Reservas", "Pagos", "Reseñas")}[lg]
    bars = ((40, 55, 48, 70, 62, 84), (30, 42, 38, 50, 66, 58), (52, 52, 70, 70, 88, 88), (60, 72, 68, 80, 86, 92))
    tiles = "".join('<div class="ov-tile"><span>%s</span><i class="ov-bars">%s</i></div>' % (
        E(n), "".join('<b style="height:%d%%"></b>' % h for h in bb)) for n, bb in zip(names, bars))
    return '<div class="ov-mock" role="img" aria-label="%s"><div class="ov-head">%s<span translate="no">OneView</span></div><div class="ov-grid">%s</div></div>' % (
        E({"en": "OneView: sales, bookings, payouts and reviews", "es": "OneView: ventas, reservas, pagos y reseñas"}[lg]), biz_icon("view", "ov-ic"), tiles)


def biz_intro(lg, I):
    left = "".join('<li>%s<span><a href="%s" translate="no">%s</a>: %s</span></li>' % (
        biz_icon(k), app_page(lg, k), APP_BY[k][1], E(t)) for k, t in I["left"][1])
    right = "".join('<li>%s<span><b translate="no">%s</b> %s</span></li>' % (biz_icon(ic), E(n), E(t)) for ic, n, t in I["right"][1])
    return ('<section class="biz-intro"><div class="wrap"><div class="bi-card"><h2>%s</h2><p class="lead">%s</p><div class="bi-cols">'
            '<div class="bi-col"><h3>%s</h3><p>%s</p><ul>%s</ul></div><div class="bi-col mine"><h3 translate="no">%s</h3><p>%s</p><ul>%s</ul></div></div></div></div></section>') % (
        E(I["h2"]), E(I["p"]), E(I["left"][0][0]), E(I["left"][0][1]), left, E(I["right"][0][0]), E(I["right"][0][1]), right)


# ── APP PAGES ────────────────────────────────────────────────────────────────────────────────
def side_html(lg, k, s, first):
    a = APP_BY[k]
    acts = []
    if s.get("primary"):
        lab, h = s["primary"]
        acts.append('<a class="btn" href="%s">%s</a>' % (L(lg, h), E(lab)))
    elif not a[3]:
        acts.append('<span class="btn soon" aria-disabled="true">%s</span>' % E(HOME[lg]["soon"]))
    if s.get("secondary"):
        lab, h = s["secondary"]
        acts.append('<a class="%s" href="%s">%s%s</a>' % ("btn ghost" if not s.get("primary") and a[3] is False else "link", L(lg, h), E(lab), EXT if h in APP_PATHS or h.startswith("/feed") else ""))
    need = ""
    if s.get("need_label"):
        need = '<p class="need-line" data-need-line data-names="%s" hidden>%s <b></b></p>' % (E(json.dumps(NEED_NAMES[lg], ensure_ascii=False)), E(s["need_label"]))
    note = '<p class="need-line" style="display:block;border-radius:16px">%s</p>' % E(s["soon_note"]) if s.get("soon_note") else ""
    out = ['<div class="side-hero"><div><h2>%s</h2><p class="lead">%s</p>%s%s<div class="oc-act">%s</div></div><figure style="--glow:%s">%s</figure></div>' % (
        E(s["h2"]), E(s["lead"]), need, note, "".join(acts), a[2], img(s["img"], s["alt"], lazy=not first))]
    if s.get("rows"):
        rr = "".join('<article class="row"><div class="row-media">%s</div><div><span class="row-tag">%s<span translate="no">%s</span></span><h3>%s</h3><p>%s</p><div class="oc-act"><a class="link" href="%s">%s</a></div></div></article>' % (
            oneview_mock(lg) if r[0] == "@oneview" else img(r[0], r[2]), biz_icon(r[5]) if len(r) > 5 else "", E(r[1]), E(r[2]), E(r[3]), L(lg, r[4][1]), E(r[4][0])) for r in s["rows"])
        out.append('<div class="how"><div class="rows">%s</div></div>' % rr)
    if s.get("chips"):
        t, p = s["chips"]
        cl = "".join('<a href="%s" data-need="%s">%s</a>' % (L(lg, "/medellin/%s/" % key), key, E(en if lg == "en" else es)) for key, en, es in JOB_NEEDS)
        out.append('<div class="chiprow"><h3>%s</h3><p>%s</p><div class="chips2">%s</div></div>' % (E(t), E(p), cl))
    how_h = {"en": "How it works", "es": "Cómo funciona"}[lg]
    out.append('<div class="how"><h3>%s</h3><ol>%s</ol></div>' % (E(how_h), "".join('<li><strong>%s</strong><p>%s</p></li>' % (E(t), E(p)) for t, p in s["steps"])))
    if s.get("band"):
        bi, bh, bp = s["band"]
        bl = '<div class="oc-act"><a class="link" href="%s">%s</a></div>' % (L(lg, s["band_link"][1]), E(s["band_link"][0])) if s.get("band_link") else ""
        out.append('<div class="band">%s<div><h3>%s</h3><p>%s</p>%s</div></div>' % (img(bi, ""), E(bh), E(bp), bl))
    feat_h = {"en": "What you get", "es": "Lo que obtiene"}[lg]
    out.append('<div class="feat"><h3>%s</h3><ul>%s</ul></div>' % (E(feat_h), "".join('<li><div><strong>%s</strong><span>%s</span></div></li>' % (E(t), E(p)) for t, p in s["feats"])))
    faq_h = {"en": "Questions people ask", "es": "Preguntas frecuentes"}[lg]
    out.append('<div class="faq"><h3>%s</h3>%s</div>' % (E(faq_h), "".join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(ans)) for q, ans in s["faq"])))
    ci, ch, cp = s["cta"]
    cacts = []
    if a[3] and a[4]:
        cacts.append('<a class="btn" href="%s">%s</a>' % (APP + a[4], E(HOME[lg]["open_x"].format(n=a[1]))))
    elif a[3]:
        cacts.append('<a class="btn" href="%s/">%s</a>' % (APP, E(HOME[lg]["open"])))
    else:
        cacts.append('<a class="btn" href="%s">%s</a>' % (L(lg, "/#contact"), E({"en": "Talk to us", "es": "Hablemos"}[lg])))
    out.append('<div class="cta-band">%s<div><h3>%s</h3><p>%s</p><div class="oc-act">%s</div></div></div><div class="side-end"></div>' % (img(ci, ""), E(ch), E(cp), "".join(cacts)))
    return "".join(out)


# Long tab labels: on a phone they take two lines, broken where the meaning breaks.
TAB_SPLIT = {"Freelancers and creators": ("Freelancers", "and creators"), "Revisar a un profesional": ("Revisar a", "un profesional")}


def tab_label(t):
    if t in TAB_SPLIT:
        return '<span class="tl">%s</span> <span class="tl">%s</span>' % tuple(E(x) for x in TAB_SPLIT[t])
    return E(t)


def build_app(lg, k):
    P = PAGES[k][lg]
    a = APP_BY[k]
    badge = '<span class="badge live">%s</span>' % E(HOME[lg]["live"]) if a[3] else '<span class="badge">%s</span>' % E(HOME[lg]["soon"])
    top = ('<section class="ap-top"><div class="wrap"><a class="crumb" href="%s">← %s</a>'
           '<div class="ap-id"><img src="%s" alt=""/><h1><span translate="no" style="display:inline;font-size:inherit;font-weight:inherit;color:inherit;margin:0">%s</span><span>%s</span></h1>%s</div></div></section>') % (
        L(lg, "/#destinations"), E(P["crumb"]), mark(k), a[1], E(P["h1s"]), badge)
    tabs = "".join('<button type="button" role="tab" id="tab-%s" aria-controls="side-%s" aria-selected="%s"%s>%s</button>' % (
        s["id"], s["id"], "true" if i == 0 else "false", "" if i == 0 else ' tabindex="-1"', tab_label(s["tab"])) for i, s in enumerate(P["sides"]))
    panes = "".join('<div class="side" id="side-%s" role="tabpanel" aria-labelledby="tab-%s" data-side="%s"><div class="wrap">%s</div></div>' % (
        s["id"], s["id"], s["id"], side_html(lg, k, s, i == 0)) for i, s in enumerate(P["sides"]))
    sides = ('<section data-sides><div class="seg-wrap"><div class="seg" role="tablist" aria-label="%s" data-at="0"><i aria-hidden="true"></i>%s</div></div>'
             '<div class="sides">%s</div></section>') % (E(P["seg"]), tabs, panes)
    order = ["oneevent", "onejob", "onehome", "oneride", "onepay", "onebusiness", "onescore", "oneagent"]
    nxt = order[(order.index(k) + 1) % len(order)]
    gh = {"en": ("Guides", "Read before you start."), "es": ("Guías", "Léalas antes de empezar.")}[lg]
    nh = {"en": "Explore another app", "es": "Conozca otra app"}[lg]
    after = ('<section class="after"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2></div>%s'
             '<div class="onecard" style="margin-top:72px"><div class="oc-top"><h3>%s</h3><a class="link" href="%s">%s</a></div><div class="oc-track">%s</div></div></div></section>') % (
        E(gh[0]), E(gh[1]), guide_cards(lg, P["guides"]), E(nh), L(lg, "/#destinations"),
        E({"en": "See all", "es": "Ver todas"}[lg]), one_card(lg, nxt, True))
    after = after[:-len("</div></section>")] + features_row(lg, compact=True) + "</div></section>"
    main = top + (biz_intro(lg, P["intro"]) if P.get("intro") else "") + sides + after
    faqs = [q for s in P["sides"] for q in s["faq"]]
    path = "/apps/%s/" % k
    url = page_url(lg, path)
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "One World", "item": page_url(lg, "/")},
            {"@type": "ListItem", "position": 2, "name": "Apps", "item": page_url(lg, "/apps/")},
            {"@type": "ListItem", "position": 3, "name": a[1], "item": url}]},
        {"@type": "SoftwareApplication", "name": a[1], "applicationCategory": "LifestyleApplication" if k not in ("onepay", "onebusiness") else ("FinanceApplication" if k == "onepay" else "BusinessApplication"),
         "operatingSystem": "Web", "url": url, "inLanguage": "en" if lg == "en" else "es-CO",
         "description": P["desc"], "publisher": {"@id": SITE + "/#org"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs]}]})
    og = "https://app.oneworldlabs.ai/og/%s.jpg" % k if k in ("onehome", "onejob", "oneevent") else P["sides"][0]["img"]
    h = head(lg, P["title"], P["desc"], path, og, ld)
    write(("apps/%s/index.html" if lg == "en" else "es/apps/%s/index.html") % k, doc(lg, h, main))


# ── BLOG INDEX ───────────────────────────────────────────────────────────────────────────────
def build_blog(lg):
    B = BLOG[lg]
    posts = sorted(POSTS[lg].values(), key=lambda p: (p["date"], p["slug"]), reverse=True)
    # newest first; among the same day, keep guides with their own photo near the top
    posts.sort(key=lambda p: (p["date"], 1 if (p["img"] or "").startswith("/blog/img/") else 0), reverse=True)
    counts = {t: 0 for t, _e, _s in TOPICS}
    for p in posts:
        for t in POST_TAGS.get(p["en"] or "", ("", None))[0].split():
            counts[t] += 1
    counts["all"] = len(posts)
    chips = topic_chips(lg, "all", counts)
    lead = posts[0]

    def tags(p):
        return POST_TAGS.get(p["en"] or "", ("", None))

    def href(p):
        return ("/blog/%s/" if lg == "en" else "/es/blog/%s/") % p["slug"]
    tg, ap = tags(lead)
    feature = ('<a class="feature-post" href="%s" data-topics="%s">%s<div><em>%s · %s</em><h2>%s</h2><p>%s</p><time datetime="%s">%s</time></div></a>') % (
        href(lead), tg, img(lead["img"], "", lazy=False), E(B["latest"]), E(APP_BY[ap][1] if ap else "One World"), E(lead["title"]), E(lead["desc"]), lead["date"], fmt_date(lg, lead["date"]))
    cards = []
    for p in posts[1:]:
        tg, ap = tags(p)
        cards.append('<a class="gcard" href="%s" data-topics="%s">%s<div><em>%s</em><h3>%s</h3><p>%s</p><time datetime="%s">%s</time></div></a>' % (
            href(p), tg, img(p["img"]), E(APP_BY[ap][1] if ap else "One World"), E(p["title"]), E(p["desc"]), p["date"], fmt_date(lg, p["date"])))
    used = []
    for p in posts:
        ap = tags(p)[1]
        if ap and ap not in used:
            used.append(ap)
    used.sort(key=lambda k: [a[0] for a in APPS].index(k))
    applinks = "".join(app_row(lg, k) for k in used)
    hub = link_row(lg, B["hub"][2], ic("onejob"), B["hub"][0], B["hub"][1], False, "/assets/v2/img/cleanteam.jpg")
    main = ('<section class="blog-hero"><div class="wrap"><span class="eyebrow">Blog</span><h1>%s</h1><p class="lead">%s</p>'
            '<nav class="filters" aria-label="%s">%s</nav>%s<div class="cards">%s</div><p class="empty" data-empty hidden>%s</p></div></section>'
            '<section class="sec"><div class="wrap"><div class="sec-head"><h2>%s</h2><p>%s</p></div><div class="app-links">%s%s</div></div></section>') % (
        E(B["h1"]), E(B["lead"]), E(B["filter_label"]), chips, feature, "".join(cards), E(B["empty"]), E(B["apps_h2"]), E(B["apps_p"]), applinks, hub)
    path = "/blog/"
    url = page_url(lg, path)
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "One World", "item": page_url(lg, "/")},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": url}]},
        {"@type": "Blog", "@id": url + "#blog", "name": B["title"].split(" | ")[0], "url": url, "description": B["desc"],
         "inLanguage": "en" if lg == "en" else "es-CO", "publisher": {"@id": SITE + "/#org"},
         "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": SITE + href(p), "datePublished": p["date"],
                       "image": SITE + p["img"], "description": p["desc"]} for p in posts]}]})
    h = head(lg, B["title"], B["desc"], path, "/og-cover.png", ld)
    write("blog/index.html" if lg == "en" else "es/blog/index.html", doc(lg, h, blog_topic_redirect(lg) + main))


# ── PASS 3 (13 Nov 2026): feature pages, apps index, OneSocial redirect, blog topic hubs ──────
TOPIC_NAME = {t: {"en": en, "es": es} for t, en, es in TOPICS}


def topic_url(lg, t):
    return ("/blog/" if lg == "en" else "/es/blog/") + ("" if t == "all" else "topic/%s/" % t)


def topic_counts(lg):
    counts = {t: 0 for t, _e, _s in TOPICS}
    for p in POSTS[lg].values():
        for t in POST_TAGS.get(p["en"] or "", ("", None))[0].split():
            counts[t] += 1
    counts["all"] = len(POSTS[lg])
    return counts


def topic_chips(lg, cur, counts=None):
    counts = counts or topic_counts(lg)
    return "".join('<a href="%s" aria-current="%s">%s<span>%d</span></a>' % (
        topic_url(lg, t), "true" if t == cur else "false", E(TOPIC_NAME[t][lg]), counts[t]) for t, _e, _s in TOPICS if counts[t])


CHEVRON = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>'
FICON = {  # distinct line icons for the cross-app features
    "one-profile": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
    "payments": '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="M2.5 10h19"/><path d="M6.5 15h4"/>',
    "messaging-and-reviews": '<path d="M4 5h16v11H9l-5 4z"/><path d="m12 7.6 1 2 2.2.3-1.6 1.5.4 2.2-2-1.1-2 1.1.4-2.2-1.6-1.5 2.2-.3z"/>',
    "onesocial": '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><path d="m15 17 2 2 4-4"/>',
}


def link_row(lg, href, mk, title, line, soon=False, thumb=None, icon=None):
    b = '<em class="badge">%s</em>' % E(HOME[lg]["soon"]) if soon else ""
    if thumb:
        lead = '<span class="lr-media"><img class="thumb" src="%s" alt="" loading="lazy"/></span>' % thumb
    else:
        lead = '<span class="lr-solo">%s</span>' % svg(icon or mk)
    return '<a class="lrow" href="%s">%s<div><b><span translate="no">%s</span>%s</b><span>%s</span></div>%s</a>' % (href, lead, E(title), b, E(line), CHEVRON)


def features_row(lg, compact=False, skip=None):
    h = {"en": "Works across every app", "es": "Funciona en todas las apps"}[lg]
    rows = [link_row(lg, L(lg, "/features/%s/" % k), ic(k), n[lg], line[lg], not live, im) for k, n, live, im, line in FEATURES if k != skip]
    score = {"en": "Your credibility, built from real jobs and reviews.", "es": "Su credibilidad, construida con trabajos y reseñas reales."}[lg]
    rows.insert(1, link_row(lg, app_page(lg, "onescore"), ic("onescore"), "OneScore", score, False, "/blog/img/badges.jpg"))
    more = {"en": "How it fits together", "es": "Cómo encaja todo"}[lg]
    return ('<div class="feat-row%s"><div class="oc-top"><h3>%s</h3><a class="link" href="%s">%s</a></div><div class="app-links">%s</div></div>') % (
        " compact" if compact else "", E(h), L(lg, "/infrastructure/"), E(more), "".join(rows))


def app_row(lg, k, thumb=True):
    a = APP_BY[k]
    return link_row(lg, app_page(lg, k), ic(k), a[1], a[6][lg][0], not a[3], a[5] if thumb else None)


APP_ORDER = ["onebusiness", "oneevent", "oneride", "onehome", "onepay", "onejob", "onescore", "oneagent"]


def crumbs(lg, items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def build_feature(lg, k):
    P = FEAT_PAGES[k][lg]
    f = FEATURE_BY[k]
    badge = '<span class="badge live">%s</span>' % E(HOME[lg]["live"]) if f[2] else '<span class="badge">%s</span>' % E(HOME[lg]["soon"])
    fc = FEAT_INDEX[lg]["crumb"]
    top = ('<section class="ap-top"><div class="wrap"><a class="crumb" href="%s">← %s</a>'
           '<div class="ap-id"><span class="ap-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg></span><h1><span style="display:inline;font-size:inherit;font-weight:inherit;color:inherit;margin:0">%s</span><span>%s</span></h1>%s</div></div></section>') % (
        L(lg, "/features/"), E(fc), FICON[k], E(P["h1"]), E(P["h1s"]), badge)
    body = '<section class="one-side"><div class="wrap">%s</div></section>' % side_html(lg, k, P["sides"][0], True)
    gh = {"en": ("Guides", "Read more."), "es": ("Guías", "Lea más.")}[lg]
    apps = '<div class="feat-row"><h3>%s</h3><div class="app-links">%s</div></div>' % (
        E(FEAT_INDEX[lg]["apps_h2"]), "".join(app_row(lg, a) for a in APP_ORDER))
    after = ('<section class="after"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2></div>%s%s%s</div></section>') % (
        E(gh[0]), E(gh[1]), guide_cards(lg, P["guides"]), features_row(lg, skip=k), apps)
    path = "/features/%s/" % k
    pre = "" if lg == "en" else "/es"
    faqs = P["sides"][0]["faq"]
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), (fc, pre + "/features/"), (P["h1"], pre + path)]),
        {"@type": "WebPage", "name": P["title"], "url": page_url(lg, path), "description": P["desc"], "inLanguage": "en" if lg == "en" else "es-CO",
         "isPartOf": {"@id": SITE + "/#site"}, "about": {"@type": "Thing", "name": P["h1"]}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]})
    write(("features/%s/index.html" if lg == "en" else "es/features/%s/index.html") % k,
          doc(lg, head(lg, P["title"], P["desc"], path, P["sides"][0]["img"], ld), top + body + after))


def build_feat_index(lg):
    X = FEAT_INDEX[lg]
    cards = "".join('<a class="gcard" href="%s">%s<div><em>%s</em><h3>%s</h3><p>%s</p></div></a>' % (
        L(lg, "/features/%s/" % k), img(im), E(HOME[lg]["live"] if live else HOME[lg]["soon"]), E(n[lg]), E(line[lg]))
        for k, n, live, im, line in FEATURES)
    apps = '<div class="feat-row"><h3>%s</h3><p>%s</p><div class="app-links">%s</div></div>' % (
        E(X["apps_h2"]), E(X["apps_p"]), "".join(app_row(lg, a) for a in APP_ORDER))
    main = ('<section class="blog-hero"><div class="wrap"><span class="eyebrow">%s</span><h1>%s</h1><p class="lead">%s</p></div></section>'
            '<section class="sec" style="padding-top:40px"><div class="wrap"><div class="cards n4">%s</div>%s</div></section>') % (
        E(X["crumb"]), E(X["h1"]), E(X["lead"]), cards, apps)
    pre = "" if lg == "en" else "/es"
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), (X["crumb"], pre + "/features/")]),
        {"@type": "CollectionPage", "name": X["title"], "url": page_url(lg, "/features/"), "description": X["desc"],
         "mainEntity": {"@type": "ItemList", "numberOfItems": len(FEATURES), "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": page_url(lg, "/features/%s/" % f[0]), "name": f[1][lg]} for i, f in enumerate(FEATURES)]}}]})
    write("features/index.html" if lg == "en" else "es/features/index.html",
          doc(lg, head(lg, X["title"], X["desc"], "/features/", "/og-cover.png", ld), main))


def build_apps_index(lg):
    X = APPS_INDEX[lg]
    live = [k for k in APP_ORDER if APP_BY[k][3]]
    soon = [k for k in APP_ORDER if not APP_BY[k][3]]

    def block(h, keys):
        return '<div class="feat-row"><h3>%s</h3><div class="app-links">%s</div></div>' % (E(h), "".join(app_row(lg, k, True) for k in keys))
    intro = {"en": ("The apps work as one suite. You keep one profile, so the work you do in one app builds your reputation in all of them.", "Why One World"),
             "es": ("Las apps funcionan como un solo conjunto. Usted tiene un solo perfil, así el trabajo que hace en una app construye su reputación en todas.", "Por qué One World")}[lg]
    main = ('<section class="blog-hero"><div class="wrap"><span class="eyebrow">Apps</span><h1>%s</h1><p class="lead">%s</p>'
            '<p class="suite-p">%s <a class="link" href="%s">%s</a></p>'
            '<div class="hero-cta" style="justify-content:flex-start"><a class="btn glass shine" href="%s/">%s</a></div></div></section>'
            '<section class="sec" style="padding-top:24px"><div class="wrap">%s%s%s</div></section>') % (
        E(X["h1"]), E(X["lead"]), E(intro[0]), L(lg, "/why/"), E(intro[1]), APP, E(HOME[lg]["open"]),
        block(X["live_h"], live), block(X["soon_h"], soon) if soon else "", features_row(lg))
    pre = "" if lg == "en" else "/es"
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), ("Apps", pre + "/apps/")]),
        {"@type": "ItemList", "name": X["title"], "numberOfItems": len(APP_ORDER), "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": {"@type": "SoftwareApplication", "name": APP_BY[k][1], **({"alternateName": "One Business"} if k == "onebusiness" else {}), "url": SITE + app_page(lg, k),
                                                               "applicationCategory": "LifestyleApplication", "operatingSystem": "Web"}} for i, k in enumerate(APP_ORDER)]}]})
    write("apps/index.html" if lg == "en" else "es/apps/index.html",
          doc(lg, head(lg, X["title"], X["desc"], "/apps/", "/og-cover.png", ld), main))


def build_redirect(lg):
    to = L(lg, "/features/onesocial/")
    t = {"en": ("OneSocial has moved", "OneSocial is now part of every One World app.", "Go to OneSocial"),
         "es": ("OneSocial cambió de lugar", "OneSocial ahora es parte de todas las apps de One World.", "Ir a OneSocial")}[lg]
    html_ = ('<!DOCTYPE html>\n<html lang="%s"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>'
             '<title>%s</title><link rel="canonical" href="%s"/><meta name="robots" content="noindex,follow"/>'
             '<meta http-equiv="refresh" content="0; url=%s"/><script>location.replace(%s+location.hash)</script></head>'
             '<body><p>%s <a href="%s">%s</a></p></body></html>\n') % (
        "en" if lg == "en" else "es-CO", E(t[0]), SITE + to, to, json.dumps(to), E(t[1]), to, E(t[2]))
    write("apps/onesocial/index.html" if lg == "en" else "es/apps/onesocial/index.html", html_)


def build_alias(lg, rel, to, words):
    """A short www address that forwards to the real page (Lee says "/business")."""
    html_ = ('<!DOCTYPE html>\n<html lang="%s"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>'
             '<title>%s</title><link rel="canonical" href="%s"/><meta name="robots" content="noindex,follow"/>'
             '<meta http-equiv="refresh" content="0; url=%s"/><script>location.replace(%s+location.search+location.hash)</script></head>'
             '<body><p><a href="%s">%s</a></p></body></html>\n') % (
        "en" if lg == "en" else "es-CO", E(words), SITE + to, to, json.dumps(to), to, E(words))
    write(rel, html_)


def build_404():
    """GitHub Pages serves /404.html for every missing address. It used to be an old copy of the
    homepage that still said OneAgent and One Business were "Coming soon"."""
    lg = "en"
    apps = "".join(app_row(lg, k, True) for k in APP_ORDER)
    main = ('<section class="blog-hero"><div class="wrap"><span class="eyebrow">404</span><h1>Page not found.</h1>'
            '<p class="lead">This page may have moved. Every One&nbsp;World app is below.</p>'
            '<div class="hero-cta" style="justify-content:flex-start"><a class="btn glass shine" href="/">Go to the homepage</a></div></div></section>'
            '<section class="sec" style="padding-top:24px"><div class="wrap"><div class="feat-row"><h3>Apps</h3><div class="app-links">%s</div></div></div></section>') % apps
    h = head(lg, "Page not found | One World", "This page may have moved. Find every One World app here.", "/404.html", "/og-cover.png", "")
    h = h.replace('<link href="%s/404.html" rel="canonical"/>' % SITE, '<meta name="robots" content="noindex"/>')
    h = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*"/>', "", h)
    write("404.html", doc(lg, h, main))


def build_hub(lg, t):
    app, words = HUBS[t]
    h1, title, desc, intro = words[lg]
    posts = sorted([p for p in POSTS[lg].values() if t in POST_TAGS.get(p["en"] or "", ("", None))[0].split()],
                   key=lambda p: (p["date"], 1 if (p["img"] or "").startswith("/blog/img/") else 0), reverse=True)
    blog = "/blog/" if lg == "en" else "/es/blog/"
    cards = guide_cards(lg, [p["slug"] for p in posts])
    see = {"en": ("The app for this", "Works across every app"), "es": ("La app para esto", "Funciona en todas las apps")}[lg]
    extra = link_row(lg, L(lg, "/features/payments/"), ic("payments"), FEATURE_BY["payments"][1][lg], FEATURE_BY["payments"][4][lg], False, FEATURE_BY["payments"][3], FICON["payments"]) if t in ("payments", "business") else ""
    main = ('<section class="blog-hero"><div class="wrap"><a class="crumb" href="%s">← Blog</a><h1 style="margin-top:12px">%s</h1><p class="lead">%s</p>'
            '<nav class="filters" aria-label="%s">%s</nav>%s'
            '<div class="feat-row"><h3>%s</h3><div class="app-links">%s%s</div></div></div></section>') % (
        blog, E(h1), E(intro), E(BLOG[lg]["filter_label"]), topic_chips(lg, t), cards, E(see[0]), app_row(lg, app), extra)
    path = "/blog/topic/%s/" % t
    pre = "" if lg == "en" else "/es"
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), ("Blog", pre + "/blog/"), (h1, pre + path)]),
        {"@type": "CollectionPage", "name": title, "url": page_url(lg, path), "description": desc, "inLanguage": "en" if lg == "en" else "es-CO",
         "isPartOf": {"@id": page_url(lg, "/blog/") + "#blog"},
         "mainEntity": {"@type": "ItemList", "numberOfItems": len(posts), "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": SITE + blog + p["slug"] + "/", "name": p["title"]} for i, p in enumerate(posts)]}}]})
    write(("blog/topic/%s/index.html" if lg == "en" else "es/blog/topic/%s/index.html") % t,
          doc(lg, head(lg, title, desc, path, posts[0]["img"] if posts else "/og-cover.png", ld), main))


def inject_posts(lg):
    """Every guide links back to its topic hubs and its app page (idempotent)."""
    root = "blog" if lg == "en" else "es/blog"
    for slug, p in POSTS[lg].items():
        f = os.path.join(ROOT, root, slug, "index.html")
        s = open(f).read()
        s = re.sub(r'<li data-hub="1">.*?</li>', "", s)
        s = re.sub(r'<section class="related" data-hubs="1">.*?</section>', "", s, flags=re.S)
        tags, app = POST_TAGS.get(p["en"] or "", ("", None))
        more = {"en": "More guides: ", "es": "Más guías: "}[lg]
        lis = "".join('<li data-hub="1"><a href="%s">%s%s</a></li>' % (topic_url(lg, t), more, E(HUBS[t][1][lg][0])) for t in tags.split() if t in HUBS)
        if app:
            a = APP_BY[app]
            lis += '<li data-hub="1"><a href="%s">%s: %s</a></li>' % (app_page(lg, app), a[1], E(a[6][lg][0]))
        s = re.sub(r'<ul class="wb-links" data-hubs-list="1">.*?</ul>', "", s, flags=re.S)
        if 'class="wb-links"' in s:
            i = s.index('class="wb-links"'); j = s.index("</ul>", i)
            s = s[:j] + lis + s[j:]
        elif '<section class="related">' in s:
            i = s.index('<section class="related">'); j = s.index("</section>", i)
            s = s[:j] + '<ul class="wb-links" data-hubs-list="1">%s</ul>' % lis + s[j:]
        else:
            h = {"en": "Keep exploring", "es": "Siga explorando"}[lg]
            s = s.replace("</main>", '<section class="related" data-hubs="1"><h2>%s</h2><ul class="wb-links">%s</ul></section></main>' % (h, lis), 1)
        open(f, "w").write(s)
    print("linked", len(POSTS[lg]), lg, "guides to their hubs")


def blog_topic_redirect(lg):
    m = {t: topic_url(lg, t) for t in HUBS}
    return '<script>(function(){try{var t=new URLSearchParams(location.search).get("topic"),m=%s;if(t&&m[t])location.replace(m[t])}catch(e){}})()</script>' % json.dumps(m)


# ── PASS 5: /why/ and company/legal pages ────────────────────────────────────────────────────
LOOP_ICONS = ['<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>', '<path d="M9 12l2 2 4-4"/><rect x="3" y="4" width="18" height="16" rx="3"/>',
              '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="M2.5 10h19"/>', '<path d="m12 3 2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.4 6.8 19.1l1-5.8L3.5 9.2l5.9-.9z"/>',
              '<path d="M4 17l5-5 4 4 7-7"/><path d="M15 9h5v5"/>']


def svg(path, cls=""):
    return '<svg%s viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (' class="%s"' % cls if cls else "", path)


def build_why(lg):
    W = WHY[lg]
    pre = "" if lg == "en" else "/es"
    hero = ('<section class="ap-top why-top"><div class="wrap"><span class="eyebrow">%s</span><h1 class="why-h1">%s</h1><p class="lead why-lead">%s</p>'
            '<div class="hero-cta" style="justify-content:flex-start"><a class="btn glass shine" href="%s/">%s</a></div></div></section>') % (
        E(W["eyebrow"]), E(W["h1"]), E(W["lead"]), APP, E(HOME[lg]["open"]))
    problem = ('<section class="sec"><div class="wrap"><div class="row"><div class="row-media">%s</div><div><h2 class="why-h2">%s</h2>%s</div></div></div></section>') % (
        img("/blog/img/promoter.jpg", ""), E(W["problem_h"]), "".join('<p class="why-p">%s</p>' % E(x) for x in W["problem_p"]))
    halves = "".join('<div class="half"><span class="ap-ic">%s</span><h3>%s</h3><p>%s</p></div>' % (svg(ic), E(h), E(p))
                     for (h, p), ic in zip(W["halves"], [FICON["onesocial"], FICON["messaging-and-reviews"]]))
    idea = ('<section class="sec"><div class="wrap"><div class="sec-head"><h2>%s</h2><p>%s</p></div><div class="halves">%s</div></div></section>') % (
        E(W["idea_h"]), E(W["idea_p"]), halves)
    steps = "".join('<li><span class="ap-ic">%s</span><b>%s</b></li>' % (svg(ic), E(t)) for t, ic in zip(W["loop"], LOOP_ICONS))
    loop = ('<section class="sec"><div class="wrap"><div class="row"><div><h2 class="why-h2">%s</h2><p class="why-p">%s</p>'
            '<ol class="loop" aria-label="%s">%s</ol></div><div class="row-media">%s</div></div></div></section>') % (
        E(W["loop_h"]), E(W["loop_p"]), E(W["loop_h"]), steps, img("/blog/img/reviews.jpg", ""))
    suite = ('<section class="sec"><div class="wrap"><div class="sec-head"><h2>%s</h2><p>%s</p><p>%s <a class="link" href="%s">%s</a></p></div><div class="app-links">%s</div></div></section>') % (
        E(W["suite_h"]), E(W["suite_p"]), E(W["infra_p"]), L(lg, "/infrastructure/"), E(W["infra_link"]), "".join(link_row(lg, app_page(lg, k), ic(k), APP_BY[k][1], line, False, APP_BY[k][5]) for k, line in W["suite"]))
    founder = ('<section class="sec"><div class="wrap"><div class="founder"><img src="/founder/founder-lee-full.jpg" alt="%s" loading="lazy"/>'
               '<div><span class="eyebrow">%s</span><h2 class="why-h2">%s</h2><p class="founder-role">%s</p><p class="why-p">%s</p>'
               '<div class="oc-act"><a class="link" href="/founder/">%s</a></div></div></div></div></section>') % (
        E(W["founder_name"]), E(W["founder_h"]), E(W["founder_name"]), E(W["founder_role"]), E(W["founder_p"]), E(W["founder_link"]))
    cta = ('<section class="sec"><div class="wrap"><div class="cta-band">%s<div><h3>%s</h3><p>%s</p><div class="oc-act"><a class="btn shine" href="%s/">%s</a></div></div></div></div></section>') % (
        img("/assets/v2/img/team.jpg", ""), E(W["cta_h"]), E(W["cta_p"]), APP, E(HOME[lg]["open"]))
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), (W["eyebrow"], pre + "/why/")]),
        {"@type": "AboutPage", "name": W["title"], "url": page_url(lg, "/why/"), "description": W["desc"], "inLanguage": "en" if lg == "en" else "es-CO",
         "about": {"@id": SITE + "/#org"}}]})
    write("why/index.html" if lg == "en" else "es/why/index.html",
          doc(lg, head(lg, W["title"], W["desc"], "/why/", "/assets/v2/img/team.jpg", ld), hero + problem + idea + loop + suite + founder + cta))


def build_infra(lg):
    X = INFRA[lg]
    pre = "" if lg == "en" else "/es"
    hero = ('<section class="ap-top why-top infra-top"><div class="wrap"><span class="eyebrow">%s</span><h1 class="why-h1">%s</h1><p class="lead why-lead">%s</p></div></section>') % (
        E(X["eyebrow"]), E(X["h1"]), E(X["lead"]))
    why = ('<section class="sec infra-sec"><div class="wrap"><div class="infra-card"><h2>%s</h2>%s</div></div></section>') % (
        E(X["why_h"]), "".join('<p>%s</p>' % E(p) for p in X["why_p"]))
    chips = "".join('<li>%s<span>%s</span></li>' % (biz_icon(k), E(t)) for k, t in zip(("sales", "marketing", "payments", "contract", "signature", "star"), X["scattered"]))
    scattered = ('<section class="sec infra-sec"><div class="wrap"><div class="infra-card"><h2>%s</h2><p>%s</p><ul class="infra-chips">%s</ul></div></div></section>') % (
        E(X["scattered_h"]), E(X["scattered_p"]), chips)
    trust = ('<section class="sec infra-sec"><div class="wrap"><div class="infra-card glow"><h2>%s</h2>%s</div></div></section>') % (
        E(X["trust_h"]), "".join('<p>%s</p>' % E(p) for p in X["trust_p"]))
    icons = {"profile": "one-profile", "score": "onescore", "social": "onesocial", "pay": "payments", "msg": "messaging-and-reviews", "contract": "contract"}
    cards = "".join('<article class="half"><span class="ap-ic">%s</span><h3>%s%s</h3><p>%s</p><div class="oc-act"><a class="link" href="%s">%s</a></div></article>' % (
        svg(ic(icons[k])), '<span translate="no">%s</span>' % E(h) if h.startswith("One") else E(h), ' <em class="badge">%s</em>' % E(HOME[lg]["soon"]) if soon else "",
        E(p), app_page(lg, "onescore") if k == "score" else L(lg, href), E(lk)) for k, h, p, lk, href, soon in X["pieces"])
    pieces = ('<section class="sec infra-sec"><div class="wrap"><div class="sec-head infra-head"><h2>%s</h2></div><div class="infra-grid">%s</div></div></section>') % (E(X["pieces_h"]), cards)
    cta = ('<section class="sec"><div class="wrap"><div class="cta-band">%s<div><h3>%s</h3><p>%s</p><div class="oc-act"><a class="btn shine" href="%s/">%s</a>'
           '<a class="btn ghost" href="%s">%s</a></div></div></div></div></section>') % (
        img("/assets/v2/img/team.jpg", ""), E(X["cta_h"]), E(X["cta_p"]), APP, E(HOME[lg]["open"]), L(lg, "/apps/"), E(X["see_apps"]))
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), (X["eyebrow"], pre + "/infrastructure/")]),
        {"@type": "WebPage", "name": X["title"], "url": page_url(lg, "/infrastructure/"), "description": X["desc"], "inLanguage": "en" if lg == "en" else "es-CO",
         "about": {"@id": SITE + "/#org"}}]})
    write("infrastructure/index.html" if lg == "en" else "es/infrastructure/index.html",
          doc(lg, head(lg, X["title"], X["desc"], "/infrastructure/", "/blog/img/ecosystem.jpg", ld), hero + why + scattered + trust + pieces + cta))


def build_doc(lg, slug):
    D = DOCS[slug][lg]
    pre = "" if lg == "en" else "/es"
    body = []
    for h, c in D["sections"]:
        if isinstance(c, tuple):
            inner = '<ul>%s</ul>' % "".join('<li>%s</li>' % E(x) for x in c[1])
        else:
            inner = "".join('<p>%s</p>' % E(x) for x in c)
        body.append('<section><h2>%s</h2>%s</section>' % (E(h), inner))
    pic = DOC_IMG.get(slug)
    fig = '<figure class="doc-fig">%s</figure>' % img(pic, "", lazy=False) if pic else ""
    main = ('<section class="ap-top"><div class="wrap doc-wrap"><span class="eyebrow">%s</span><h1 class="doc-h1">%s</h1><p class="lead">%s</p>%s'
            '<div class="doc-card">%s</div></div></section><div style="height:72px"></div>') % (
        E(D["eyebrow"]), E(D["h1"]), E(D["lead"]), fig, "".join(body))
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        crumbs(lg, [("One World", pre + "/"), (D["h1"], pre + "/%s/" % slug)]),
        {"@type": "WebPage", "name": D["title"], "url": page_url(lg, "/%s/" % slug), "description": D["desc"], "inLanguage": "en" if lg == "en" else "es-CO"}]})
    write(("%s/index.html" if lg == "en" else "es/%s/index.html") % slug,
          doc(lg, head(lg, D["title"], D["desc"], "/%s/" % slug, pic or "/og-cover.png", ld), main))


if __name__ == "__main__":
    for lg in ("en", "es"):
        build_home(lg)
        for k in PAGES:
            build_app(lg, k)
        build_blog(lg)
        for k in FEAT_PAGES:
            build_feature(lg, k)
        build_feat_index(lg)
        build_apps_index(lg)
        build_redirect(lg)
        build_alias(lg, "business/index.html" if lg == "en" else "es/business/index.html", L(lg, "/apps/onebusiness/"),
                    "OneBusiness" if lg == "en" else "OneBusiness")
        for t in HUBS:
            build_hub(lg, t)
        inject_posts(lg)
        build_why(lg)
        build_infra(lg)
        for d in DOCS:
            build_doc(lg, d)
    build_404()
