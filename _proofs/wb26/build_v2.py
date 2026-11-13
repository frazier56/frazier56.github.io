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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "05c5c9b"          # the commit whose header/footer we keep
SITE = "https://www.oneworldlabs.ai"
V = "v2a"                  # cache-buster for v2.css / v2.js
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
        header=cut(s, "<header", "</header>"),
        footer=cut(s, "<footer", "</footer>"),
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
    return headhtml + p["body"] + p["header"] + '<main id="main">' + main + "</main>" + (p["vaia_box"] if home else "") + p["footer"] + tail(lg, home)


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
    phones = "".join(
        '<div class="phone" role="group" aria-label="%s" style="--hue:%s"><div class="scr">%s<div class="lane-bar"><i></i><span translate="no">%s</span></div>'
        '<div class="post"><strong>%s</strong><span>%s</span><b>%s</b></div><div class="tabbar" aria-hidden="true"><u></u><u></u><u class="c"></u><u></u><u></u></div></div></div>' % (
            APP_BY[k][1], APP_BY[k][2], img(src, "", lazy=False), APP_BY[k][1], E(t[lg][0]), E(t[lg][1]), E(t[lg][2]))
        for k, src, t in SCREENS)
    dots = "".join('<button type="button" aria-label="%s"></button>' % E(H["dot"].format(n=APP_BY[k][1])) for k, _s, _t in SCREENS)
    hero = ('<section class="hero2"><div class="wrap"><div class="hero-copy"><h1>%s</h1><p class="hero-sub">%s</p><p class="lead">%s</p>'
            '<div class="hero-cta"><a class="btn" href="%s/">%s%s</a></div></div>'
            '<div class="stage" data-screens data-start="1" role="region" aria-label="%s"><div class="screens">%s</div><div class="dots">%s</div></div></div></section>') % (
        E(H["h1"]), E(H["sub"]), E(H["lead"]), APP, PHONE, E(H["open"]), E(H["stage_label"]), phones, dots)

    cats, panels = [], []
    for cid, pic, app, words, opts, kind in EXPLORER:
        name, small, para = words[lg]
        cats.append('<button class="ex-cat" type="button" aria-expanded="false" aria-controls="ex-%s">%s<span>%s</span><small>%s</small></button>' % (
            cid, img(pic), E(name), E(small)))
        main_opts = [o for o in opts if not (kind == "chips" and "side=work" in o[0])]
        work_opts = [o for o in opts if kind == "chips" and "side=work" in o[0]]
        lis = "".join('<li><a href="%s">%s</a></li>' % (L(lg, h), E(lab[lg])) for h, lab in main_opts)
        a = APP_BY[app]
        via = '<p class="ex-app"><img src="%s" alt=""/><span>%s <strong translate="no">%s</strong>%s</span></p>' % (
            mark(app), E(H["via"].capitalize()), a[1], "" if a[3] else " · " + E(H["soon"]))
        if cid == "grow":
            via = '<p class="ex-app"><img src="%s" alt=""/><span>%s <strong translate="no">OneJob</strong> · <strong translate="no">OneBusiness</strong></span></p>' % (mark("onejob"), E(H["via"].capitalize()))
        panels.append('<div class="ex-panel" id="ex-%s">%s<div class="ex-body"><button class="ex-back" type="button" hidden>%s%s</button><h3>%s</h3><p>%s</p>'
                      '<ul class="ex-opts%s">%s</ul>%s%s</div></div>' % (
                          cid, img(pic), LEFT, E(H["back"]), E(name), E(para), " chips" if kind == "chips" else "", lis,
                          ('<p class="ex-sub">%s</p><ul class="ex-opts">%s</ul>' % (E({"en": "Or get hired", "es": "O consiga trabajo"}[lg]),
                           "".join('<li><a href="%s">%s</a></li>' % (L(lg, h), E(lab[lg])) for h, lab in work_opts))) if work_opts else "", via))
    order = ["oneevent", "onejob", "onehome", "oneride", "onepay", "onebusiness", "onescore", "onesocial", "oneagent"]
    onecard = ('<div class="onecard" data-onecard><div class="oc-top"><h3>%s</h3><div class="oc-nav"><button type="button" data-prev aria-label="%s">%s</button>'
               '<span class="oc-count" aria-live="polite">1 / %d</span><button type="button" data-next aria-label="%s">%s</button></div></div>'
               '<div class="oc-track" role="region" aria-roledescription="carousel" aria-label="%s">%s</div></div>') % (
        E(H["oc_h3"]), E(H["prev"]), LEFT, len(order), E(H["next"]), RIGHT, E(H["oc_h3"]),
        "".join(one_card(lg, k, i == 0) for i, k in enumerate(order)))
    explore = ('<section class="sec explore" id="destinations"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p></div>'
               '<div class="ex" data-explorer><div class="ex-cats">%s</div>%s</div>%s</div></section>') % (
        E(H["ex_eyebrow"]), E(H["ex_h2"]), E(H["ex_p"]), "".join(cats), "".join(panels), onecard)

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

    steps = "".join('<div><b>0%d</b><h4>%s</h4><p>%s</p></div>' % (i + 1, E(t), E(p)) for i, (t, p) in enumerate(H["steps"]))
    oneid = ('<section class="sec explore"><div class="wrap oneid"><div class="oneid-mark"><img src="/mark-oneworld.png" alt="" loading="lazy"/></div>'
             '<div><span class="eyebrow">%s</span><h2 style="font-size:clamp(32px,4vw,52px);font-weight:800;letter-spacing:-.045em;line-height:1.05">%s</h2><div class="steps3">%s</div></div></div></section>') % (
        E(H["id_eyebrow"]), E(H["id_h2"]), steps)
    guides = ('<section class="sec"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2></div>%s'
              '<p class="more"><a class="btn ghost" href="%s">%s</a></p></div></section>') % (
        E(H["g_eyebrow"]), E(H["g_h2"]), guide_cards(lg, HOME_GUIDES[lg]), L(lg, "/blog/"), E(H["g_all"]))
    contact = '<div class="wrap" style="padding-bottom:40px">' + PARTS[lg]["contact"].replace('<section class="contact" id="contact">', '<section class="contact" id="contact" style="max-width:none;margin:0;padding:0">') + "</div>"
    main = hero + explore + biz + oneid + guides + contact
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
    if a[3]:
        cacts.append('<a class="btn" href="%s">%s</a>' % (APP + a[4], E(HOME[lg]["open_x"].format(n=a[1]))))
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
    order = ["oneevent", "onejob", "onehome", "oneride", "onepay", "onebusiness"]
    nxt = order[(order.index(k) + 1) % len(order)]
    gh = {"en": ("Guides", "Read before you start."), "es": ("Guías", "Léalas antes de empezar.")}[lg]
    nh = {"en": "Explore another app", "es": "Conozca otra app"}[lg]
    after = ('<section class="after"><div class="wrap"><div class="sec-head"><span class="eyebrow">%s</span><h2>%s</h2></div>%s'
             '<div class="onecard" style="margin-top:72px"><div class="oc-top"><h3>%s</h3><a class="link" href="%s">%s</a></div><div class="oc-track">%s</div></div></div></section>') % (
        E(gh[0]), E(gh[1]), guide_cards(lg, P["guides"]), E(nh), L(lg, "/#destinations"),
        E({"en": "See all", "es": "Ver todas"}[lg]), one_card(lg, nxt, True))
    main = top + sides + after
    faqs = [q for s in P["sides"] for q in s["faq"]]
    path = "/apps/%s/" % k
    url = page_url(lg, path)
    ld = ldjson({"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "One World", "item": page_url(lg, "/")},
            {"@type": "ListItem", "position": 2, "name": "Apps" if lg == "en" else "Apps", "item": SITE + "/apps/"},
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
    chips = "".join('<a href="?topic=%s" data-topic="%s" aria-current="%s">%s<span>%d</span></a>' % (
        t, t, "true" if t == "all" else "false", E(en if lg == "en" else es), counts[t]) for t, en, es in TOPICS if counts[t])
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
    applinks = "".join('<a href="%s"><img src="%s" alt=""/><div><span translate="no" style="font-size:16px;font-weight:750;color:var(--ink)">%s</span><span>%s</span></div></a>' % (
        app_page(lg, k), mark(k), APP_BY[k][1], E(APP_BY[k][6][lg][0] + ("" if APP_BY[k][3] else " · " + HOME[lg]["soon"]))) for k in used)
    hub = '<a href="%s"><img src="%s" alt=""/><div><span style="font-size:16px;font-weight:750;color:var(--ink)">%s</span><span>%s</span></div></a>' % (B["hub"][2], mark("onejob"), E(B["hub"][0]), E(B["hub"][1]))
    main = ('<section class="blog-hero"><div class="wrap"><span class="eyebrow">Blog</span><h1>%s</h1><p class="lead">%s</p>'
            '<nav class="filters" data-filters aria-label="%s">%s</nav>%s<div class="cards">%s</div><p class="empty" data-empty hidden>%s</p></div></section>'
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
    write("blog/index.html" if lg == "en" else "es/blog/index.html", doc(lg, h, main))


if __name__ == "__main__":
    for lg in ("en", "es"):
        build_home(lg)
        for k in PAGES:
            build_app(lg, k)
        build_blog(lg)
