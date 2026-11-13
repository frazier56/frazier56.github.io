#!/usr/bin/env python3
"""Homepage restructure (12 Nov 2026, orchestrator's pick; Lee can veto).

Problem: from the top of the homepage a visitor could not quickly reach the app, and "apps" vs
"agency/services" told two stories. Now: the hero has an Open the app button and two doors
(Use One World: the consumer apps; Run a business: OneBusiness with OneVoice, OnePage, OneApp),
a "What do you need in Medellín?" search sits right under it, the platform-vs-agency section is
replaced by one business section, and the destination cards no longer offer "Open app" for
apps that are still coming soon (OneSocial, OneScore, OneBusiness: Lee's launch list).
Idempotent on the committed index.html: run once, then build_es.py.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = "https://app.oneworldlabs.ai"
ES = {}


def t(key, en, es):
    ES[key] = es
    return en


TILES = [  # Lee's order: live apps first, then coming soon
    ("OneEvent", A + "/events", "Events and tickets", "Eventos y boletas", "#E2711D", False),
    ("OneJob", A + "/jobs", "Hire or get hired", "Contrate o consiga trabajo", "#17A45C", False),
    ("OneHome", A + "/home", "Homes to rent or buy", "Vivienda para arrendar o comprar", "#0EA5E9", False),
    ("OneRide", A + "/rides", "Book a ride", "Pida un viaje", "#3a3a50", False),
    ("OnePay", A + "/pay", "Get paid by link or QR", "Cobre por enlace o QR", "#b4793e", False),
    ("OneScore", "/apps/onescore/", "Your reputation in one score", "Su reputación en un puntaje", "#E0A21F", True),
]
CHIPS = [("dj", "DJ", "DJ"), ("cleaning", "Cleaning", "Limpieza"), ("private-driver", "Driver", "Conductor"),
         ("videographer", "Videographer", "Videógrafo"), ("photographer", "Photographer", "Fotógrafo"),
         ("makeup-artist", "Makeup", "Maquillaje"), ("private-chef", "Private chef", "Chef privado"),
         ("personal-trainer", "Trainer", "Entrenador"), ("dog-walker", "Dog walker", "Paseador de perros"),
         ("babysitter", "Babysitter", "Niñera")]


def tiles():
    out = ""
    for i, (name, href, en, es, col, soon) in enumerate(TILES):
        out += ('<a class="app-tile%s" href="%s" style="--accent:%s"><strong translate="no">%s</strong>'
                '<span data-i18n="khtile%d">%s</span>%s</a>' % (
                    " soon" if soon else "", href, col, name, i, t("khtile%d" % i, en, es),
                    '<em data-i18n="khsoon">%s</em>' % t("khsoon", "Coming soon", "Próximamente") if soon else ""))
    return out


def hero():
    return (
        '<section class="hero home-doors"><div class="hero-copy">'
        '<h1 data-i18n="k039715448">Big ideas.<br/>Everyday life.<br/><em class="headline choice-1">One world.</em></h1>'
        '<p class="lead" data-i18n="khlead">%s</p>'
        '<div class="actions"><a class="button" data-i18n="khopen" href="%s/">%s</a>'
        '<a class="text-link" data-i18n="khbiz" href="#business">%s</a></div>'
        '<div class="ow-stores" data-slot="store-badges" hidden=""></div></div>'
        '<aside class="world-panel doors"><div class="recess-row"><strong data-i18n="khuse">%s</strong>'
        '<a data-i18n="khall" href="%s/">%s</a></div><div class="app-tiles">%s</div>'
        '<a class="door-biz" href="#business"><span class="eyebrow" data-i18n="khrun">%s</span>'
        '<strong data-i18n="khbizt">%s</strong><span data-i18n="khbizp">%s</span></a></aside></section>'
        % (t("khlead", "One app for events, work, homes, rides and payments, in Medellín and the United States.",
             "Una sola app para eventos, trabajo, vivienda, viajes y pagos, en Medellín y Estados Unidos."),
           A, t("khopen", "Open the app ↗", "Abrir la app ↗"), t("khbiz", "I run a business →", "Tengo un negocio →"),
           t("khuse", "Use One World", "Use One World"), A, t("khall", "Open ↗", "Abrir ↗"), tiles(),
           t("khrun", "Run a business", "Para su negocio"), t("khbizt", "OneBusiness →", "OneBusiness →"),
           t("khbizp", "AI call answering, a website and your own app.", "Atención de llamadas con IA, un sitio web y su propia app.")))


def search():
    chips = "".join('<a data-i18n="khc%d" href="/medellin/%s/">%s</a>' % (i, slug, t("khc%d" % i, en, es))
                    for i, (slug, en, es) in enumerate(CHIPS))
    opts = "".join('<option value="%s"></option>' % en for _, en, _ in CHIPS)
    return (
        '<section class="home-search" id="find"><form action="/medellin/" class="find-form" data-find role="search">'
        '<label for="find-q"><span class="eyebrow" data-i18n="khfind">%s</span></label>'
        '<div class="find-row"><input autocomplete="off" data-i18n-attr="placeholder:khph" id="find-q" list="find-list" name="q" placeholder="%s" type="search"/>'
        '<button class="button" data-i18n="khgo" type="submit">%s</button></div><datalist id="find-list">%s</datalist>'
        '<p class="wb-chips">%s</p></form></section>'
        % (t("khfind", "What do you need in Medellín?", "¿Qué necesita en Medellín?"),
           t("khph", "DJ, cleaning, driver, photographer…", "DJ, limpieza, conductor, fotógrafo…"),
           t("khgo", "Find", "Buscar"), opts, chips))


def business():
    cards = [("OneVoice", "/onevoice/", "#2E6BE6", t("khv", "Answer every call.", "Conteste todas las llamadas."),
              t("khvp", "An AI receptionist that answers 24/7, books appointments and texts back.", "Una recepcionista con IA que contesta 24/7, agenda citas y responde por mensaje.")),
             ("OnePage", "/onepage/", "#D6338B", t("khp", "A website that works.", "Un sitio web que funciona."),
              t("khpp", "Built with AI, then hosted, updated and managed for you.", "Creado con IA y luego alojado, actualizado y administrado por usted… por nosotros.")),
             ("OneApp", "https://oneapp.oneworldlabs.ai/", "#8E2F6B", t("kha", "Your own app.", "Su propia app."),
              t("khap", "Your business in the App Store and Google Play.", "Su negocio en App Store y Google Play."))]
    ES["khpp"] = "Creado con IA y luego alojado, actualizado y administrado por nosotros."
    arts = "".join(
        '<article class="destination" style="--accent:%s"><div class="destination-top"><span translate="no">%s</span></div>'
        '<h3 data-i18n="%s">%s</h3><p data-i18n="%s">%s</p><div class="actions"><a href="%s" data-i18n="khmore">%s</a></div></article>'
        % (col, name, k1, h, k2, p, href, t("khmore", "Learn more →", "Conozca más →"))
        for (name, href, col, h, p), (k1, k2) in zip(cards, [("khv", "khvp"), ("khp", "khpp"), ("kha", "khap")]))
    return (
        '<section id="business"><div class="section-heading"><span class="eyebrow" data-i18n="khbe">%s</span>'
        '<h2 data-i18n="khbh">%s</h2><p data-i18n="khbp">%s</p></div><div class="destinations">%s</div>'
        '<p class="actions"><a class="button" data-i18n="khbb" href="/services/">%s</a></p></section>'
        % (t("khbe", "OneBusiness · Run a business", "OneBusiness · Para su negocio"),
           t("khbh", "Your business,<0/>handled.", "Su negocio,<0/>bien atendido.").replace("<0/>", "<br/>"),
           t("khbp", "Calls answered, a website that works and your own app, set up and managed with you.",
             "Llamadas contestadas, un sitio web que funciona y su propia app, configurados y gestionados con usted."),
           arts, t("khbb", "See everything for business →", "Vea todo para su negocio →")))


def main():
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    if "home-doors" in s:
        raise SystemExit("already applied")
    i = s.index('<section class="hero">'); j = s.index('<section id="destinations">')
    s = s[:i] + hero() + search() + s[j:]
    i = s.index('<section id="divisions">'); j = s.index('<section class="connected">')
    s = s[:i] + business() + s[j:]
    # coming-soon apps never get an "Open app" link (Lee, 5 Oct + 12 Nov 2026)
    for key, app, path in (("k41336e6e4", "OneSocial", "social"), ("k99475bc3f", "OneScore", "onescore"), ("k3990ea43f", "OneBusiness", "business")):
        old = re.search(r'<a aria-label="Open %s" data-i18n-attr="aria-label:%s" href="https://app.oneworldlabs.ai/%s">Open app ↗</a>' % (app, key, path), s)
        assert old, app
        s = s.replace(old.group(0), '<span class="soon-tag">Coming soon</span>')
    for key, nk, app, es in (("k847614cae", "khsoc", "OneSocial", "<0>Conozca OneSocial →</0><1>Próximamente</1>"),
                             ("k813d6564b", "khsco", "OneScore", "<0>Conozca OneScore →</0><1>Próximamente</1>"),
                             ("k83ea9ac01", "khsbz", "OneBusiness", "<0>Conozca OneBusiness →</0><1>Próximamente</1>")):
        assert s.count('data-i18n="%s"' % key) == 1, key
        s = s.replace('data-i18n="%s"' % key, 'data-i18n="%s"' % nk); ES[nk] = es
    # the six destination cards' "Open app" label templates lose their second slot for those three
    s = s.replace('<p data-i18n="k182c53fb3">Six places to begin. Choose a destination and make it yours.</p>',
                  '<p data-i18n="khdest">%s</p>' % t("khdest", "Start with the app that fits what you want to do. Some are still coming soon.",
                                                   "Empiece con la app que se ajusta a lo que quiere hacer. Algunas llegan pronto."))
    # the find box: send a typed need to its Medellín page (no JS: lands on the hub)
    s = s.replace("</body></html>", FIND_JS + "</body></html>", 1)
    open(p, "w", encoding="utf-8").write(s)
    for lang in ("co", "es"):
        f = os.path.join(ROOT, "assets/i18n/%s.json" % lang)
        d = json.load(open(f, encoding="utf-8")); d.update(ES)
        open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False))
    u = os.path.join(ROOT, "_proofs/wb22/es-usted.json")
    d = json.load(open(u, encoding="utf-8")); d.update(ES)
    json.dump(d, open(u, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


FIND_JS = """<script>(function(){var f=document.querySelector('[data-find]');if(!f)return;
var W=[['dj','dj','disc'],['cleaning','clean','maid','limpi','aseo','emplead','servicio dom'],['private-driver','driv','chof','conduc','transp','aeropuerto','airport'],
['videographer','video'],['photographer','photo','foto'],['makeup-artist','makeup','make-up','maquill'],['private-chef','chef','cook','cocin','catering'],
['personal-trainer','train','entren','gym','fitness'],['dog-walker','dog','perro','pasead'],['babysitter','baby','nann','niñer','niner','sitter']];
f.addEventListener('submit',function(e){e.preventDefault();var q=(f.q.value||'').toLowerCase(),to='';
for(var i=0;i<W.length&&!to;i++)for(var j=1;j<W[i].length;j++)if(q.indexOf(W[i][j])>-1){to=W[i][0];break}
var es=document.documentElement.getAttribute('data-ow-static')==='co';location.href=(es?'/es':'')+'/medellin/'+(to?to+'/':'');});})();</script>
"""

if __name__ == "__main__":
    main()
