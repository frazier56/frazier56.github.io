#!/usr/bin/env python3
"""
BUILD THE SIX PER-APP PAGES — /apps/<key>/index.html
============================================================================================
Lee, 13 Aug 2026:

  *"When you type in the URL for OneHome — onehome.oneworldlabs.ai should take you to the actual
  page for OneHome, and it doesn't work at all. So each page has its own page now where it
  explains what that app does. And that particular page should have a call to action to download
  the app at the top. And then when you download that app, it will take you directly to that
  page — if you're on the OneJob page and you click download the app, it's gonna be coded to
  prioritise OneJob."*

── WHY THIS IS A GENERATOR AND NOT SIX HAND-WRITTEN FILES ──────────────────────────────────
Six pages that must carry the same header, the same 200-line stylesheet, the same language
menu, the same theme toggle and the same footer is six copies of everything that has ever been
fixed once. The `_proofs/backgrounds.html` round alone changed the field on three files; doing
that to nine would guarantee one gets missed.

So the shell of every page — everything from <!doctype> through </header>, and the whole footer —
is LIFTED VERBATIM from `apps/index.html` at build time. Change the header on the apps page, run
this again, and all six inherit it. Only the middle is per-app, and that comes from the table
below, which is the single place any product's marketing copy lives.

── WHAT EACH PAGE CARRIES ─────────────────────────────────────────────────────────────────
  1. The download / open call to action AT THE TOP, before the explanation. Lee asked for it
     there specifically, and it is right: somebody who arrived from an advert for this app has
     already decided, and making them scroll past prose to act is a tax on the most valuable
     visitor on the page.
  2. What the app actually does, in a paragraph a person would read out loud.
  3. Four concrete things it does — not features, outcomes.
  4. The same call to action again at the bottom, for the person who read.

Every CTA points at `app.oneworldlabs.ai/<path>` — the product's OWN doorway, not the origin.
That is what makes the app "sit right there" in Your World afterwards: mounting a product's shell
records it as the default (see the note in shell/screens/AppShell.tsx). No query parameter to
lose, no marketing-side co-operation needed.
"""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / "apps" / "index.html"
src  = SRC.read_text(encoding="utf-8")

HEAD = src[:src.index("</header>") + len("</header>")]
FOOT = src[src.index("<footer"):]

APPS = [
  dict(key="onejob", name="OneJob", path="/jobs", hue=("#2563EB", "#1D4ED8", "#93C5FD"),
       tag="The work marketplace",
       lede="Get hired and get paid, without chasing anybody for the money.",
       body="OneJob is where small jobs get agreed, done and paid for. You post what you need or "
            "you take work that is offered; both sides sign the same simple contract; the money is "
            "held from the moment the job is agreed and released when it is finished. No invoice, "
            "no awkward follow-up message a fortnight later.",
       points=["A signed agreement on every job, in plain language",
               "The payment held safely before the work starts",
               "Reviews that only a completed, paid job can produce",
               "Everything you have earned in one place at tax time"]),
  dict(key="onescore", name="OneScore", path="/onescore", hue=("#7C3AED", "#6D28D9", "#C4B5FD"),
       tag="Credibility you own",
       lede="A reputation that follows you, instead of one you rebuild on every platform.",
       body="OneScore turns what you have actually done into a number you can show anybody. "
            "Completed work, verified credentials, real reviews and connections all count towards "
            "it. It is yours, it moves with you across every One World app, and nobody can buy a "
            "better one.",
       points=["One score built from work you genuinely completed",
               "Licences and certificates checked, not just claimed",
               "Reviews carried in from the places you already work",
               "Free forever — it costs nothing to be credible"]),
  dict(key="oneevent", name="OneEvent", path="/events", hue=("#DB2777", "#BE185D", "#F9A8D4"),
       tag="Events and tickets",
       lede="Run an event and keep what you sell.",
       body="OneEvent handles the whole thing: the page, the tickets, the door and the money. "
            "People buy from a link you send, scan in on the day, and your payout arrives without "
            "a fortnight of reconciliation. Small enough for a room above a bar, sturdy enough for "
            "a room of five hundred.",
       points=["Sell tickets from a link, with no shopfront to build",
               "Scan people in at the door from your phone",
               "Pay the people who worked the event, in the app",
               "See what sold, when, and through whom"]),
  dict(key="onesocial", name="OneSocial", path="/social", hue=("#0891B2", "#0E7490", "#67E8F9"),
       tag="Your platforms, connected",
       lede="Every account you already have, adding up to one professional identity.",
       body="OneSocial connects the platforms you are already on and turns the audience you have "
            "already built into credibility somebody can verify. One profile, one link to send, and "
            "a following that finally counts for something outside the app it lives in.",
       points=["Connect the accounts you already post to",
               "One public profile that proves the following is real",
               "Post to several places without opening several apps",
               "Followers that count towards your OneScore"]),
  dict(key="oneagent", name="OneAgent", path="/agent", hue=("#B91C1C", "#991B1B", "#FCA5A5"),
       tag="Your middleman", soon=True,
       lede="Somebody in your corner, finding and negotiating the work.",
       body="OneAgent is representation for people who have never had any — a real middleman who "
            "brings you opportunities, handles the awkward conversation about money, and takes a "
            "share only when you get paid. It is being built now.",
       points=["Work brought to you instead of hunted down",
               "Somebody else has the money conversation",
               "Paid on your results, never up front",
               "Built on the same One ID as everything else"]),
  dict(key="onehome", name="OneHome", path="/home", hue=("#0D9488", "#0F766E", "#5EEAD4"),
       tag="Rent or buy a home",
       lede="A home with a real contract behind it, instead of a chat thread and a promise.",
       body="OneHome is renting and buying in Colombia, done properly. To rent: a signed lease, a "
            "deposit handled the way Colombian law actually requires, and move-in photographs both "
            "sides agreed to. To buy: the registered sale history of the property — what it "
            "genuinely last sold for, from the national registry — which nobody in the country has "
            "been able to show a buyer before.",
       points=["A signed lease and move-in photos both sides accepted",
               "The property's real registered sale prices, from the registry",
               "Filter on things listings never state — the bed, the AC, the view",
               "Prices in pesos or dollars at the official daily rate"]),
]

TPL = """
    <main class="relative z-10 pt-24 md:pt-28">
      <section class="container mx-auto px-4 max-w-3xl text-center mb-16 md:mb-20">
        <p class="text-xs font-bold tracking-widest uppercase mb-3" style="color:{hb}">{tag}</p>
        <h1 class="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.05] mb-5">{name}{soon_badge}</h1>
        <p class="text-lg sm:text-xl md:text-2xl font-semibold tracking-tight max-w-2xl mx-auto mb-8 leading-snug">{lede}</p>

        <!-- THE CALL TO ACTION, AT THE TOP. Lee asked for it here specifically, and somebody who
             followed an advert for this app has already decided — making them scroll past prose
             before they can act taxes the most valuable visitor on the page. -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <a href="https://app.oneworldlabs.ai{path}" class="btn-clay w-full sm:w-auto h-12 px-7 text-base inline-flex items-center justify-center rounded-full font-bold text-white">
            {cta}
          </a>
          <a href="/apps/" class="w-full sm:w-auto h-12 px-6 inline-flex items-center justify-center rounded-full font-semibold text-muted-foreground hover:text-foreground transition-colors">
            See all six apps
          </a>
        </div>
        <p class="text-xs sm:text-sm text-muted-foreground/80 mt-4">One login for every app · Free to start · No credit card</p>
      </section>

      <section class="container mx-auto px-4 max-w-3xl mb-16 md:mb-20">
        <div class="frost rounded-3xl p-6 md:p-9">
          <p class="text-base md:text-lg leading-relaxed text-muted-foreground">{body}</p>
          <ul class="mt-7 grid gap-3 sm:grid-cols-2">
            {points}
          </ul>
        </div>
      </section>

      <section class="container mx-auto px-4 max-w-3xl text-center mb-24 md:mb-32">
        <h2 class="text-2xl md:text-3xl font-extrabold tracking-tight mb-4">{closer}</h2>
        <p class="text-muted-foreground max-w-xl mx-auto mb-7 leading-relaxed">
          Your One ID works across all six apps and the services we run for you. Set it up once
          on {name} and you are already signed in everywhere else.
        </p>
        <a href="https://app.oneworldlabs.ai{path}" class="btn-clay h-12 px-7 inline-flex items-center justify-center rounded-full font-bold text-white">
          {cta}
        </a>
      </section>
    </main>
"""

POINT = ('<li class="flex items-start gap-2.5 text-[15px] leading-snug">'
         '<span class="mt-1 shrink-0" style="color:{hb}">'
         '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 13 4 4L19 7"/></svg>'
         '</span><span>{t}</span></li>')

written = []
for a in APPS:
    hb, hd, hl = a["hue"]
    soon = a.get("soon")
    head = HEAD
    # per-page title, description and canonical — six pages sharing one <title> is one page to a
    # search engine, which is the whole reason these exist as separate addresses.
    head = re.sub(r"<title>.*?</title>",
                  f"<title>{a['name']} — {a['tag']} | One World Labs</title>", head, count=1, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")',
                  lambda m: m.group(1) + a["lede"] + " " + a["body"][:110] + "…" + m.group(2),
                  head, count=1)
    head = head.replace('</head>',
        f'<link rel="canonical" href="https://www.oneworldlabs.ai/apps/{a["key"]}/">\n</head>', 1)
    # the page takes the product's own hue, so the frost, buttons and accents match the app
    head = head.replace('<body', f'<body style="--hb:{hb};--hd:{hd};--hl:{hl}"', 1)

    cta = "Read about it" if soon else f"Open {a['name']}"
    body = TPL.format(
        hb=hb, tag=a["tag"], name=a["name"], lede=a["lede"], body=a["body"], path=a["path"], cta=cta,
        soon_badge=('<span class="align-middle ml-3 rounded-full border-2 px-3 py-1 text-[13px] '
                    'font-black uppercase tracking-widest" style="border-color:' + hb + ';color:' + hb + '">'
                    'Coming soon</span>') if soon else "",
        points="\n            ".join(POINT.format(hb=hb, t=t) for t in a["points"]),
        closer=("Not open yet — but your One ID already is."
                if soon else f"Start with {a['name']}."))

    out = ROOT / "apps" / a["key"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + body + FOOT, encoding="utf-8")
    written.append(str(out.relative_to(ROOT)))

print("\n".join(written))
print(f"\n{len(written)} pages built from apps/index.html's shell")
