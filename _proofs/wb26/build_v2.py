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
PAGES.update(APP_PAGES3)
for _k, _n, _live, _img, _line in FEATURES:
    if _k not in APP_BY:
        APP_BY[_k] = (_k, _n["en"], "#0D9488", _live, None, _img, {"en": (_line["en"], _line["en"]), "es": (_line["es"], _line["es"])})

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "05c5c9b"          # the commit whose header/footer we keep
SITE = "https://www.oneworldlabs.ai"
V = "v2d"                  # cache-buster for v2.css / v2.js
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
        ld=re.search(r'<script type="application/ld\+json">.*?</script>', s, re.S).group(0),
        body=body_open.replace("<body>", '<body class="v2">', 1),
        header=cut(s, "<header", "</header>").replace('<a href="/blog/">Blog</a>', '<a href="/es/blog/">Blog</a>') if lg == "es" else cut(s, "<header", "</header>"),
        footer=cut(s, "<footer", "</footer>").replace('<a href="/blog/">Lea el blog</a>', '<a href="/es/blog/">Lea el blog</a>') if lg == "es" else cut(s, "<footer", "</footer>"),
        contact=cut(s, '<section class="contact" id="contact">', "</section>"),
        widget=re.search(r'<script[^>]*widgets\.leadconnectorhq\.com/loader\.js[^>]*></script>', s).group(0),
        vaia=re.search(r'<script>/\* feature flag vaia.*?</script>', s, re.S).group(0),
        vaia_box=cut(s, '<div class="asleep" id="vaia-widget">', "<footer", incl=False),
    )

APP_PATHS = {"/home", "/jobs", "/events", "/rides", "/pay"}

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
    if h.startswith("/features/") or h == "/apps/":
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
    t = ('<script src="/assets/ow-site.js?v=wb23" defer></script>\n'
         '<script src="/assets/site-theme.js?v=09f8469a" defer></script>\n'
         '<script src="/assets/v2/v2.js?v=%s" defer></script>\n') % V
    if home:
        t += PARTS[lg]["widget"] + "\n" + PARTS[lg]["vaia"] + "\n"
    return t + "</body></html>\n"


def doc(lg, headhtml, main, home=False):
    p = PARTS[lg]
    more = {"en": (("/apps/", "All apps"), ("/features/", "Features"), ("/blog/", "Guides by topic")),
            "es": (("/es/apps/", "Todas las apps"), ("/es/features/", "Funciones"), ("/es/blog/", "Guías por tema"))}[lg]
    foot = p["footer"].replace("</footer>", '<nav class="foot-more" aria-label="%s">%s</nav></footer>' % (
        "More" if lg == "en" else "Más", "".join('<a href="%s">%s</a>' % (h, E(t)) for h, t in more)))
    return headhtml + p["body"] + p["header"] + '<main id="main">' + main + "</main>" + (p["vaia_box"] if home else "") + foot + tail(lg, home)


def write(rel, s):
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
    return ('<article class="oc" aria-roledescription="slide">%s<div class="oc-body"><div class="oc-id"><img src="%s" alt=""/><strong translate="no">%s</strong>%s</div>'
            '<h4>%s</h4><p>%s</p><div class="oc-act">%s</div></div></article>') % (
        img(a[5], "", lazy=not first), mark(k), a[1], badge, E(title), E(line), act)


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
            '<div class="slide"><div class="phone" role="group" aria-label="%s" style="--hue:%s"><div class="scr">%s<div class="lane-bar"><i></i><span translate="no">%s</span></div>'
            '<div class="post"><strong>%s</strong><span>%s</span>%s</div></div></div>'
            '<a class="link more-link" href="%s" aria-label="%s">%s</a></div>' % (
                a[1], a[2], img(src, "", lazy=False), a[1], E(title), E(sub), act,
                app_page(lg, k), E(H["learn_x"].format(n=a[1])), E(H["learn"])))
    hero = ('<section class="hero2"><div class="wrap"><div class="hero-copy"><h1>%s</h1><p class="hero-sub">%s</p><p class="lead">%s</p>'
            '<div class="hero-cta"><a class="btn glass" href="%s/">%s%s</a></div></div></div>'
            '<div class="apps2" id="destinations"><div class="wrap"><h2 class="apps2-h">%s</h2></div>'
            '<div class="stage" data-screens data-start="0" role="region" aria-roledescription="carousel" aria-label="%s"><div class="screens">%s</div>'
            '<div class="oc-nav below"><button type="button" data-prev aria-label="%s">%s</button>'
            '<span class="oc-count" aria-live="polite">1 / %d</span><button type="button" data-next aria-label="%s">%s</button></div></div></div></section>') % (
        E(H["h1"]), E(H["sub"]), E(H["lead"]), APP, PHONE, E(H["open"]),
        E(H["oc_h3"]), E(H["oc_h3"]), "".join(slides), E(H["prev"]), LEFT, len(SCREENS), E(H["next"]), RIGHT)

    rows = []
    for app, pic, link, words in STORY:
        tag, h3, p, lab = words[lg]
        rows.append('<article class="row"><div class="row-media">%s</div><div><span class="row-tag"><img src="%s" alt=""/><span translate="no">%s</span></span>'
                    '<h3>%s</h3><p>%s</p><div class="oc-act"><a class="link" href="%s">%s</a></div></div></article>' % (
                        img(pic, h3), mark(app), E(tag), E(h3), E(p), L(lg, link), E(lab)))
    biz = ('<section class="sec" id="business"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p></div>'
           '<div class="rows">%s</div><div class="biz-note"><div><h3>%s</h3><p>%s</p></div><div class="oc-act"><a class="btn" href="%s">%s</a><a class="link" href="%s">%s</a></div></div></div></section>') % (
        E(H["biz_eyebrow"]), E(H["biz_h2"]), E(H["biz_p"]), "".join(rows), E(H["note_h3"]), E(H["note_p"]),
        L(lg, "/services/"), E(H["note_a"]), L(lg, "/#contact"), E(H["note_b"]))

    steps = "".join('<div class="step"><b>%d</b><div><h4>%s</h4><p>%s</p></div></div>' % (i + 1, E(t), E(p)) for i, (t, p) in enumerate(H["steps"]))
    oneid = ('<section class="sec sec-oneid"><div class="wrap oneid"><div class="oneid-mark"><img src="/mark-oneworld.png" alt="" loading="lazy"/></div>'
             '<div><span class="eyebrow">%s</span><h2 style="font-size:clamp(32px,4vw,52px);font-weight:800;letter-spacing:-.045em;line-height:1.05">%s</h2><div class="steps3">%s</div>%s</div></div></section>') % (
        E(H["id_eyebrow"]), E(H["id_h2"]), steps, features_row(lg, compact=True))
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
    out = ['<div class="side-hero"><div><h2>%s</h2><p class="lead">%s</p>%s%s<div class="oc-act">%s</div></div><figure>%s</figure></div>' % (
        E(s["h2"]), E(s["lead"]), need, note, "".join(acts), img(s["img"], s["alt"], lazy=not first))]
    if s.get("rows"):
        rr = "".join('<article class="row"><div class="row-media">%s</div><div><span class="row-tag"><span translate="no">%s</span></span><h3>%s</h3><p>%s</p><div class="oc-act"><a class="link" href="%s">%s</a></div></div></article>' % (
            img(p, h3), E(tag), E(h3), E(t), L(lg, lk[1]), E(lk[0])) for p, tag, h3, t, lk in s["rows"])
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


def build_app(lg, k):
    P = PAGES[k][lg]
    a = APP_BY[k]
    badge = '<span class="badge live">%s</span>' % E(HOME[lg]["live"]) if a[3] else '<span class="badge">%s</span>' % E(HOME[lg]["soon"])
    top = ('<section class="ap-top"><div class="wrap"><a class="crumb" href="%s">← %s</a>'
           '<div class="ap-id"><img src="%s" alt=""/><h1><span translate="no" style="display:inline;font-size:inherit;font-weight:inherit;color:inherit;margin:0">%s</span><span>%s</span></h1>%s</div></div></section>') % (
        L(lg, "/#destinations"), E(P["crumb"]), mark(k), a[1], E(P["h1s"]), badge)
    tabs = "".join('<button type="button" role="tab" id="tab-%s" aria-controls="side-%s" aria-selected="%s"%s>%s</button>' % (
        s["id"], s["id"], "true" if i == 0 else "false", "" if i == 0 else ' tabindex="-1"', E(s["tab"])) for i, s in enumerate(P["sides"]))
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
    after = after[:-len("</div></section>")] + features_row(lg) + "</div></section>"
    main = top + sides + after
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
    hub = link_row(lg, B["hub"][2], mark("onejob"), B["hub"][0], B["hub"][1], False, "/assets/v2/img/cleanteam.jpg")
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
        lead = '<span class="lr-media"><img class="thumb" src="%s" alt="" loading="lazy"/>%s</span>' % (
            thumb, ('<span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg></span>' % icon) if icon
            else '<img class="lr-mk" src="%s" alt=""/>' % mk)
    else:
        lead = '<img class="lr-mk solo" src="%s" alt=""/>' % mk
    return '<a class="lrow" href="%s">%s<div><b><span translate="no">%s</span>%s</b><span>%s</span></div>%s</a>' % (href, lead, E(title), b, E(line), CHEVRON)


def features_row(lg, compact=False, skip=None):
    h = {"en": "Works across every app", "es": "Funciona en todas las apps"}[lg]
    links = "".join(link_row(lg, L(lg, "/features/%s/" % k), mark(k), n[lg], line[lg], not live, im, FICON[k])
                    for k, n, live, im, line in FEATURES if k != skip)
    return '<div class="feat-row%s"><h3>%s</h3><div class="app-links">%s</div></div>' % (" compact" if compact else "", E(h), links)


def app_row(lg, k, thumb=True):
    a = APP_BY[k]
    return link_row(lg, app_page(lg, k), mark(k), a[1], a[6][lg][0], not a[3], a[5] if thumb else None)


APP_ORDER = ["oneevent", "onejob", "onehome", "oneride", "onepay", "onebusiness", "onescore", "oneagent"]


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
    main = ('<section class="blog-hero"><div class="wrap"><span class="eyebrow">Apps</span><h1>%s</h1><p class="lead">%s</p>'
            '<div class="hero-cta" style="justify-content:flex-start"><a class="btn glass" href="%s/">%s</a></div></div></section>'
            '<section class="sec" style="padding-top:24px"><div class="wrap">%s%s%s</div></section>') % (
        E(X["h1"]), E(X["lead"]), APP, E(HOME[lg]["open"]), block(X["live_h"], live), block(X["soon_h"], soon), features_row(lg))
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


def build_hub(lg, t):
    app, words = HUBS[t]
    h1, title, desc, intro = words[lg]
    posts = sorted([p for p in POSTS[lg].values() if t in POST_TAGS.get(p["en"] or "", ("", None))[0].split()],
                   key=lambda p: (p["date"], 1 if (p["img"] or "").startswith("/blog/img/") else 0), reverse=True)
    blog = "/blog/" if lg == "en" else "/es/blog/"
    cards = guide_cards(lg, [p["slug"] for p in posts])
    see = {"en": ("The app for this", "Works across every app"), "es": ("La app para esto", "Funciona en todas las apps")}[lg]
    extra = link_row(lg, L(lg, "/features/payments/"), mark("payments"), FEATURE_BY["payments"][1][lg], FEATURE_BY["payments"][4][lg], False, FEATURE_BY["payments"][3], FICON["payments"]) if t in ("payments", "business") else ""
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
        for t in HUBS:
            build_hub(lg, t)
        inject_posts(lg)
