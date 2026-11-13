#!/usr/bin/env python3
"""WB-21 + WB-25 (12 Nov 2026): Medellín service pages and price guides, English and Spanish.

Plain static HTML Google can read. One page per service and language, a Medellín hub per
language, and four price-guide articles per language. Content and sources: content.py.
Re-run from the repo root:  python3 _proofs/wb21/build_city.py
"""
import html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import SERVICES, PROS, S, UPDATED, UPDATED_EN, UPDATED_ES, APP_FIND, PROFILE
from articles import ARTICLES

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://www.oneworldlabs.ai"
V = "09f8469a"
E = html.escape

def city_path(lang, slug=None):
    base = "/medellin/" if lang == "en" else "/es/medellin/"
    return base + (slug + "/" if slug else "")

def art_path(lang, a):
    return ("/blog/%s/" % a["slug_en"]) if lang == "en" else ("/es/blog/%s/" % a["slug_es"])

T = {
 "en": dict(lang="en", html="en", static="en", skip="Skip to content", tag="A world of possibilities.",
            nav=[("/#destinations", "The platform"), ("/services/", "The agency"), ("/blog/", "Blog"), ("/#contact", "Contact")],
            signin_long="Sign in with One ID", signin="Sign in", signed="Signed in", open="Open my apps", out="Sign out",
            lang_label="Language and country", acct="Your One ID", main="Main", footer_label="Footer",
            f_eyebrow="One account. Many possibilities.",
            f_nav=[("/#destinations", "Explore the apps"), ("/services/", "Explore the agency"), ("/blog/", "Read the blog"), ("mailto:support@oneworldlabs.ai", "Get in touch")],
            privacy="Privacy Policy", terms="Terms of Service", home="Home", hub="Medellín", ogl="en_US", ogl_alt="es_CO"),
 "es": dict(lang="es", html="es-CO", static="co", skip="Ir al contenido", tag="Un mundo de posibilidades.",
            nav=[("/es/#destinations", "La plataforma"), ("/es/services/", "La agencia"), ("/blog/", "Blog"), ("/es/#contact", "Contacto")],
            signin_long="Inicie sesión con One ID", signin="Iniciar sesión", signed="Sesión iniciada", open="Abrir mis apps", out="Cerrar sesión",
            lang_label="Idioma y país", acct="Su One ID", main="Principal", footer_label="Pie de página",
            f_eyebrow="Una cuenta. Muchas posibilidades.",
            f_nav=[("/es/#destinations", "Explore las apps"), ("/es/services/", "Explore la agencia"), ("/blog/", "Lea el blog"), ("mailto:support@oneworldlabs.ai", "Contáctenos")],
            privacy="Política de privacidad", terms="Términos del servicio", home="Inicio", hub="Medellín", ogl="es_CO", ogl_alt="en_US"),
}

HEAD_SCRIPTS = """<script>
/* One ID / OAuth redirect-catcher — same block as every page that can be returned to after sign-in. */
(function () {
  var h = location.hash || "", q = location.search || "";
  if (!/access_token|refresh_token|error_description|type=recovery/.test(h) && !/[?&]code=/.test(q)) return;
  if (location.hostname === "app.oneworldlabs.ai") return;
  location.replace("https://app.oneworldlabs.ai/" + q + h);
})();
</script>
<script>(function(){var t=null;try{t=localStorage.getItem("owl_site_theme")}catch(e){}if(t!=="dark")t="light";document.documentElement.setAttribute("data-theme",t)})()</script>
<script src="/assets/ow-flags.js"></script>
<script src="/assets/oneid-bridge.js?v=%s"></script>
<link rel="stylesheet" href="/assets/site.css?v=wb21">
""" % V

ICON_APPS = '<svg aria-hidden="true" class="ow-ic" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24"><rect height="7" rx="1.5" width="7" x="3" y="3"></rect><rect height="7" rx="1.5" width="7" x="14" y="3"></rect><rect height="7" rx="1.5" width="7" x="3" y="14"></rect><rect height="7" rx="1.5" width="7" x="14" y="14"></rect></svg>'
ICON_OUT = '<svg aria-hidden="true" class="ow-ic" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="m16 17 5-5-5-5"></path><path d="M21 12H9"></path></svg>'


def header(t):
    nav = "".join('<a href="%s">%s</a>' % (h, E(x)) for h, x in t["nav"])
    home = "/" if t["lang"] == "en" else "/es/"
    return ('<a class="skip" href="#main">%s</a><header><a aria-label="One World" class="brand" href="%s">'
            '<img alt="" aria-hidden="true" class="brand-icon-light" height="48" src="/assets/brand-icon-oneworld.png" width="48"/>'
            '<img alt="" aria-hidden="true" class="brand-icon-dark" height="48" src="/assets/brand-icon-oneworld-dark.png" width="48"/>'
            '<span class="brand-lockup"><span class="brand-name" translate="no">ne<span class="brand-world">World</span></span>'
            '<span class="brand-small">%s</span></span></a><nav aria-label="%s">%s</nav><div class="ow-tools"><div class="ow-pop">'
            '<button aria-controls="ow-lang-menu" aria-expanded="false" aria-haspopup="menu" aria-label="%s" class="ow-chip" id="ow-lang-btn" type="button"><span class="ow-code">%s</span></button>'
            '<div class="ow-menu" hidden="" id="ow-lang-menu" role="menu"></div></div>'
            '<a class="button small" href="https://app.oneworldlabs.ai/signin" id="ow-acct-out"><span class="ow-long">%s</span><span class="ow-short">%s</span></a>'
            '<div class="ow-pop" hidden="" id="ow-acct-in"><button aria-controls="ow-acct-menu" aria-expanded="false" aria-haspopup="menu" aria-label="%s" class="ow-chip ow-avatar" id="ow-acct-btn" type="button">·</button>'
            '<div class="ow-menu" hidden="" id="ow-acct-menu" role="menu"><div class="ow-who"><strong>%s</strong><span>One ID</span></div>'
            '<a class="ow-open" href="https://app.oneworldlabs.ai/" role="menuitem">%s<span>%s</span></a>'
            '<button class="ow-signout" role="menuitem" type="button">%s<span>%s</span></button></div></div></div></header>'
            % (E(t["skip"]), home, E(t["tag"]), E(t["main"]), nav, E(t["lang_label"]), "EN" if t["lang"] == "en" else "CO",
               E(t["signin_long"]), E(t["signin"]), E(t["acct"]), E(t["signed"]), ICON_APPS, E(t["open"]), ICON_OUT, E(t["out"])))


def footer(t):
    nav = "".join('<a href="%s">%s</a>' % (h, E(x)) for h, x in t["f_nav"])
    return ('<footer><div><span class="eyebrow">%s</span><strong>One World.</strong></div><nav aria-label="%s">%s</nav>'
            '<p>© 2026 One World Labs · <a href="https://app.oneworldlabs.ai/privacy">%s</a> · <a href="https://app.oneworldlabs.ai/terms">%s</a></p></footer>'
            '<script src="/assets/ow-site.js?v=wb22" defer></script>\n<script src="/assets/site-theme.js?v=%s" defer></script>\n'
            % (E(t["f_eyebrow"]), E(t["footer_label"]), nav, E(t["privacy"]), E(t["terms"]), V))


def page(lang, path, alt_en, alt_es, title, desc, body, graph, og_type="website"):
    t = T[lang]
    url = SITE + path
    alts = ""
    if alt_en and alt_es:
        alts = ('<link rel="alternate" hreflang="en" href="%s%s"/><link rel="alternate" hreflang="es" href="%s%s"/>'
                '<link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, alt_en, SITE, alt_es, SITE, alt_en))
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    return ('<!DOCTYPE html>\n<html data-ow-prefix="" data-ow-static="%s" data-ow-v="%s" lang="%s"><head><meta charset="utf-8"/>\n%s'
            '<meta content="width=device-width,initial-scale=1" name="viewport"/><title>%s</title><meta content="%s" name="description"/>'
            '<link href="%s" rel="canonical"/>%s<meta content="%s" property="og:title"/><meta content="%s" property="og:description"/>'
            '<meta content="%s" property="og:url"/><meta content="%s" property="og:type"/><meta content="%s" property="og:locale"/><meta content="%s" property="og:locale:alternate"/>'
            '<meta content="One World Labs" property="og:site_name"/><meta content="https://app.oneworldlabs.ai/og/onejob.jpg" property="og:image"/>'
            '<meta content="summary_large_image" name="twitter:card"/><meta content="%s" name="twitter:title"/><meta content="%s" name="twitter:description"/>'
            '<meta content="https://app.oneworldlabs.ai/og/onejob.jpg" name="twitter:image"/>'
            '<link href="/owl-manifest.webmanifest" rel="manifest"/><link href="/apple-touch-icon.png" rel="apple-touch-icon"/><meta content="#FAFAF8" id="theme-color-meta" name="theme-color"/>'
            '<script type="application/ld+json">%s</script></head><body>%s<main id="main">%s</main>%s</body></html>\n'
            % (t["static"], V, t["html"], HEAD_SCRIPTS, E(title), E(desc), url, alts, E(title), E(desc), url, og_type,
               t["ogl"], t["ogl_alt"], E(title), E(desc), ld.replace("</", "<\\/"), header(t), body, footer(t)))


def write(path, content):
    f = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w", encoding="utf-8").write(content)
    return f


def crumbs(lang, items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(items)]}


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def src_link(key, lang):
    title, url, n_en, n_es = S[key]
    return '<a href="%s" rel="noopener">%s</a> (%s)' % (E(url), E(title), E(n_en if lang == "en" else n_es))


L = {
 "en": dict(eyebrow="Medellín · <span class=\"wb-nw\">Updated %s</span>" % UPDATED_EN, back="All services in Medellín",
            cost="What %s costs in Medellín", typical="Typical ranges", th=("What", "Typical range", "Source"),
            caveat="Typical ranges from public listings and guides, checked on %s. They are not One World prices: each pro sets their own, and you agree the price with them." % UPDATED_EN,
            drives="What changes the price", how="How hiring through OneJob works", pros_h="On OneJob in Medellín",
            pros_p="Public One World profiles whose owners say they do this work in Medellín. Open a profile to see their work and reviews.",
            law="Before you hire", faq="Questions people ask", more="More services in Medellín", guide="Read the full price guide",
            find="Find %s in OneJob ↗", sources="Sources",
            safety="One World does not run background or criminal-record checks. Read the profile and reviews, ask for references, and meet the person before the first job.",
            child="For childcare, meet the sitter with your children present before the first job, call their references, and never share door codes or keys until you are comfortable."),
 "es": dict(eyebrow="Medellín · <span class=\"wb-nw\">Actualizada el %s</span>" % UPDATED_ES, back="Todos los servicios en Medellín",
            cost="Cuánto cuesta %s en Medellín", typical="Rangos habituales", th=("Qué", "Rango habitual", "Fuente"),
            caveat="Rangos habituales tomados de anuncios y guías públicas, revisados el %s. No son precios de One World: cada profesional fija el suyo y usted acuerda el precio con esa persona." % UPDATED_ES,
            drives="Qué cambia el precio", how="Cómo se contrata por OneJob", pros_h="En OneJob en Medellín",
            pros_p="Perfiles públicos de One World cuyos dueños dicen que hacen este trabajo en Medellín. Abra un perfil para ver su trabajo y sus reseñas.",
            law="Antes de contratar", faq="Preguntas frecuentes", more="Más servicios en Medellín", guide="Lea la guía de precios completa",
            find="Encuentre %s en OneJob ↗", sources="Fuentes",
            safety="One World no hace verificaciones de antecedentes ni de pasado judicial. Revise el perfil y las reseñas, pida referencias y conozca a la persona antes del primer servicio.",
            child="Para el cuidado de niños, conozca a la niñera con sus hijos presentes antes del primer servicio, llame a sus referencias y no comparta claves ni llaves hasta sentirse tranquilo."),
}

HOW = {
 "en": [("Find the person.", "Search pros in OneJob, or open a profile someone sent you. Profiles show what the person does, their photos and videos, and reviews from past jobs."),
        ("Put it in writing.", "Start a contract with the date, hours, place, what is included and the price, in pesos or dollars. Both of you accept it in the app."),
        ("Pay your way.", "Card payments made through OneJob on eligible contracts are held and released after you both mark the job complete. To pay a person in pesos with Nequi or PSE, use OnePay, part of the same app, by link or QR code. Cash or a direct transfer is up to you, but OneJob does not hold that money."),
        ("Leave a review.", "After the job, each of you reviews the other, so the next person can decide with more to go on.")],
 "es": [("Encuentre a la persona.", "Busque profesionales en OneJob o abra un perfil que alguien le envió. Los perfiles muestran qué hace la persona, sus fotos y videos, y reseñas de trabajos anteriores."),
        ("Déjelo por escrito.", "Cree un contrato con la fecha, las horas, el lugar, lo que incluye y el precio, en pesos o en dólares. Ambos lo aceptan en la app."),
        ("Pague como prefiera.", "Los pagos con tarjeta hechos por OneJob en contratos elegibles quedan retenidos y se liberan cuando ambos marcan el trabajo como terminado. Para pagarle a una persona en pesos con Nequi o PSE, use OnePay, parte de la misma app, por enlace o código QR. El efectivo o una transferencia directa son decisión suya, pero OneJob no retiene ese dinero."),
        ("Deje una reseña.", "Después del trabajo, cada uno califica al otro, para que la próxima persona decida con más información.")],
}
ONESCORE = {"en": "Coming soon: OneScore, a credibility score built from a member's connected accounts, reviews and paid work.",
            "es": "Próximamente: OneScore, un puntaje de credibilidad construido con las cuentas conectadas, las reseñas y el trabajo pagado de cada miembro."}


def how_block(lang):
    li = "".join("<li><strong>%s</strong> %s</li>" % (E(a), E(b)) for a, b in HOW[lang])
    return "<h2>%s</h2><ol>%s</ol><p>%s</p>" % (E(L[lang]["how"]), li, E(ONESCORE[lang]))


def price_table(svc, lang):
    th = L[lang]["th"]
    rows = "".join("<tr><td>%s</td><td><strong>%s</strong></td><td>%s</td></tr>" % (
        E(r[0] if lang == "en" else r[2]), E(r[1] if lang == "en" else r[3]), src_link(r[4], lang)) for r in svc["prices"])
    return '<div class="wb-table"><table><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>' % (
        E(th[0]), E(th[1]), E(th[2]), rows)


def pros_block(svc, lang):
    pros = PROS.get(svc["slug"])
    if not pros: return ""
    li = "".join('<li><a href="%s%s">%s</a> · %s</li>' % (PROFILE, pid, E(name), E(en if lang == "en" else es)) for pid, name, en, es in pros)
    return "<h2>%s</h2><p>%s</p><ul>%s</ul>" % (E(L[lang]["pros_h"]), E(L[lang]["pros_p"]), li)


def svc_links(lang, skip=None):
    return '<ul class="wb-links">%s</ul>' % "".join(
        '<li><a href="%s">%s</a></li>' % (city_path(lang, s["slug"]), E(s[lang]["h1"].replace(" in Medellín", "").replace(" en Medellín", "")))
        for s in SERVICES if s["slug"] != skip)


def find_button(svc, lang):
    return '<p class="actions"><a class="button" href="%s">%s</a></p>' % (APP_FIND, E(L[lang]["find"] % svc[lang]["a"]))


def city_page(svc, lang):
    c, l = svc[lang], L[lang]
    path = city_path(lang, svc["slug"])
    art = next((a for a in ARTICLES if a["key"] == svc.get("article")), None)
    drivers = "".join("<li>%s</li>" % E(x) for x in svc["drivers_" + lang])
    note = svc.get("note_" + lang)
    law = svc.get("law_" + lang)
    safety = ""
    if svc.get("safety") or svc.get("child"):
        safety = "<h2>%s</h2>" % E(l["law"]) + ("<p>%s</p>" % E(law) if law else "") + "<p>%s</p>" % E(l["safety"]) + (
            "<p>%s</p>" % E(l["child"]) if svc.get("child") else "")
    elif law:
        safety = "<h2>%s</h2><p>%s</p>" % (E(l["law"]), E(law))
    faq = svc["faq_" + lang]
    faq_html = "".join("<h3>%s</h3><p>%s</p>" % (E(q), E(a)) for q, a in faq)
    guide = ('<p><a href="%s"><strong>%s →</strong></a></p>' % (art_path(lang, art), E(l["guide"]))) if art else ""
    body = ('<article class="blog-article wb-page"><nav><a href="%s">← %s</a></nav><div><span>%s</span></div><h1>%s</h1><p>%s</p>%s<div>'
            '<h2>%s</h2><p class="wb-sub">%s</p>%s<p class="wb-note">%s</p>%s%s'
            '<h2>%s</h2><ul>%s</ul>%s%s%s<h2>%s</h2>%s<h2>%s</h2>%s%s</div></article>'
            % (city_path(lang), E(l["back"]), l["eyebrow"], E(c["h1"]), E(c["intro"]), find_button(svc, lang),
               E(l["cost"] % c["a"]), E(l["typical"]), price_table(svc, lang), E(l["caveat"]),
               ("<p>%s</p>" % E(note)) if note else "", guide,
               E(l["drives"]), drivers, safety, how_block(lang), pros_block(svc, lang),
               E(l["faq"]), faq_html, E(l["more"]), svc_links(lang, svc["slug"]), find_button(svc, lang)))
    en_p, es_p = city_path("en", svc["slug"]), city_path("es", svc["slug"])
    graph = [crumbs(lang, [(T[lang]["home"], "/" if lang == "en" else "/es/"), ("Medellín", city_path(lang)), (c["h1"], path)]),
             {"@type": "Service", "@id": SITE + path + "#service", "name": c["h1"], "serviceType": c["name"],
              "description": c["desc"], "url": SITE + path, "inLanguage": T[lang]["html"],
              "areaServed": {"@type": "City", "name": "Medellín", "containedInPlace": {"@type": "Country", "name": "Colombia"}},
              "provider": {"@id": SITE + "/#org"},
              "availableChannel": {"@type": "ServiceChannel", "serviceUrl": APP_FIND, "name": "OneJob"}},
             faq_ld(faq)]
    return write(path, page(lang, path, en_p, es_p, c["title"], c["desc"], body, graph))


HUB = {
 "en": dict(title="Hire local pros in Medellín: prices and guides (2026) | One World",
            desc="Typical 2026 prices and hiring guides for DJs, cleaners, videographers, drivers, photographers, makeup artists, chefs, trainers, dog walkers and babysitters in Medellín.",
            h1="Hire local pros in Medellín", intro="Ten services people in Medellín hire most often. Each guide shows typical 2026 prices from public sources, what changes the price, and how to agree and pay the job through OneJob.",
            services="Services", guides="Price guides"),
 "es": dict(title="Contrate profesionales en Medellín: precios y guías (2026) | One World",
            desc="Precios habituales 2026 y guías para contratar DJ, empleadas por días, videógrafos, conductores, fotógrafos, maquilladoras, chefs, entrenadores, paseadores de perros y niñeras en Medellín.",
            h1="Contrate profesionales en Medellín", intro="Diez servicios que más se contratan en Medellín. Cada guía muestra precios habituales de 2026 tomados de fuentes públicas, qué cambia el precio y cómo acordar y pagar el servicio por OneJob.",
            services="Servicios", guides="Guías de precios"),
}


def hub_page(lang):
    h = HUB[lang]; path = city_path(lang)
    guides = '<ul class="wb-links">%s</ul>' % "".join('<li><a href="%s">%s</a></li>' % (art_path(lang, a), E(a[lang]["short"])) for a in ARTICLES)
    body = ('<article class="blog-article wb-page"><div><span>%s</span></div><h1>%s</h1><p>%s</p>%s<div><h2>%s</h2>%s<h2>%s</h2>%s%s</div></article>'
            % (L[lang]["eyebrow"], E(h["h1"]), E(h["intro"]),
               '<p class="actions"><a class="button" href="%s">%s</a></p>' % (APP_FIND, E("Open OneJob ↗" if lang == "en" else "Abrir OneJob ↗")),
               E(h["services"]), svc_links(lang), E(h["guides"]), guides, how_block(lang)))
    graph = [crumbs(lang, [(T[lang]["home"], "/" if lang == "en" else "/es/"), ("Medellín", path)]),
             {"@type": "CollectionPage", "name": h["h1"], "url": SITE + path, "inLanguage": T[lang]["html"],
              "hasPart": [{"@type": "WebPage", "name": s[lang]["h1"], "url": SITE + city_path(lang, s["slug"])} for s in SERVICES]}]
    return write(path, page(lang, path, city_path("en"), city_path("es"), h["title"], h["desc"], body, graph))


AL = {
 "en": dict(back="Back to the blog", backhref="/blog/", eyebrow="Price guide · Medellín · <span class=\"wb-nw\">%s</span>" % UPDATED_EN, short="Short answer",
            table="Typical 2026 prices", faq="Questions people ask", sources="Sources", city="Hire in Medellín",
            hire="See the %s page for Medellín", disclaimer="Prices are typical ranges from the public sources listed below, checked on %s. They change over time and each pro sets their own price. One World does not set or guarantee any of these prices." % UPDATED_EN),
 "es": dict(back="Medellín", backhref="/es/medellin/", eyebrow="Guía de precios · Medellín · <span class=\"wb-nw\">%s</span>" % UPDATED_ES, short="Respuesta corta",
            table="Precios habituales 2026", faq="Preguntas frecuentes", sources="Fuentes", city="Contratar en Medellín",
            hire="Vea la página de %s en Medellín", disclaimer="Los precios son rangos habituales tomados de las fuentes públicas que se listan abajo, revisadas el %s. Cambian con el tiempo y cada profesional fija su propio precio. One World no fija ni garantiza ninguno de estos precios." % UPDATED_ES),
}


def article_page(a, lang):
    c, l = a[lang], AL[lang]
    svc = next(s for s in SERVICES if s.get("article") == a["key"])
    path = art_path(lang, a)
    secs = "".join("<h2>%s</h2>%s" % (E(h), b) for h, b in c["sections"])
    srcs = "".join("<li>%s</li>" % src_link(k, lang) for k in a["sources"])
    faq = c["faq"]
    body = ('<article class="blog-article wb-page"><nav><a href="%s">← %s</a></nav><div><span>%s</span></div><h1>%s</h1><p>%s</p><div>'
            '<h2>%s</h2><p>%s</p><h2>%s</h2>%s<p class="wb-note">%s</p>%s%s<h2>%s</h2>%s<h2>%s</h2><p><a href="%s"><strong>%s →</strong></a></p>%s'
            '<h2>%s</h2><ul>%s</ul></div></article>'
            % (l["backhref"], E(l["back"]), l["eyebrow"], E(c["h1"]), E(c["dek"]), E(l["short"]), c["answer"],
               E(l["table"]), price_table(svc, lang), E(l["disclaimer"]), secs, how_block(lang),
               E(l["faq"]), "".join("<h3>%s</h3><p>%s</p>" % (E(q), E(x)) for q, x in faq),
               E(l["city"]), city_path(lang, svc["slug"]), E(l["hire"] % svc[lang]["name"]), svc_links(lang, svc["slug"]),
               E(l["sources"]), srcs))
    graph = [crumbs(lang, [(T[lang]["home"], "/" if lang == "en" else "/es/"), ("Blog" if lang == "en" else "Medellín", "/blog/" if lang == "en" else "/es/medellin/"), (c["h1"], path)]),
             {"@type": "BlogPosting", "headline": c["h1"], "description": c["desc"], "datePublished": UPDATED, "dateModified": UPDATED,
              "inLanguage": T[lang]["html"], "author": {"@type": "Organization", "name": "One World Labs", "@id": SITE + "/#org"},
              "publisher": {"@id": SITE + "/#org"}, "mainEntityOfPage": SITE + path,
              "citation": [S[k][1] for k in a["sources"]]},
             faq_ld(faq)]
    return write(path, page(lang, path, art_path("en", a), art_path("es", a), c["title"], c["desc"], body, graph, "article"))


def all_paths():
    out = []
    for lang in ("en", "es"):
        out.append(city_path(lang))
        out += [city_path(lang, s["slug"]) for s in SERVICES]
        out += [art_path(lang, a) for a in ARTICLES]
    return out


if __name__ == "__main__":
    n = 0
    for lang in ("en", "es"):
        hub_page(lang); n += 1
        for s in SERVICES: city_page(s, lang); n += 1
        for a in ARTICLES: article_page(a, lang); n += 1
    print("pages written:", n)
