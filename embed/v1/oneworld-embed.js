/*! One World site embed v1 — a member's OneEvent events and reviews on their own website.
 *
 * Drop-in (renders cards for you):
 *   <script src="https://www.oneworldlabs.ai/embed/v1/oneworld-embed.js" defer></script>
 *   <div data-oneworld-events="victoria-yoga"></div>
 *   <div data-oneworld-reviews="victoria-yoga"></div>
 *
 * Custom design (the site draws its own cards from the same data):
 *   OneWorldEmbed.load("victoria-yoga", { lang: "es" }).then(function (data) { ... })
 *   Reviews: show data.reviews (One World) and data.google as two separate blocks, each with its own
 *   average and count. Never show data.summary (a blend of both) — Google's Places policy forbids
 *   mixing Google ratings with non-Google ones. data.summary stays in the feed only for old pages.
 *
 * Options: data-lang="es|en" on the element (default: <html lang>), data-limit="6",
 * data-tz="America/Bogota" (time zone for events that have none), data-endpoint on the <script>.
 * Style hooks: CSS variables --owe-accent, --owe-card, --owe-ink, --owe-radius, --owe-shadow;
 * every element carries an .owe-* class. Fonts and colours inherit from the site.
 * No keys, no cookies, no tracking. Text is always escaped. Only https links are followed.
 */
(function (w, d) {
  "use strict";
  if (w.OneWorldEmbed) return;
  var cur = d.currentScript;
  var ENDPOINT = (cur && cur.getAttribute("data-endpoint")) ||
    (w.OneWorldEmbedConfig && w.OneWorldEmbedConfig.endpoint) ||
    "https://wseblryyqxawvbjmylbo.supabase.co/functions/v1/site-embed";
  var cache = {};

  function langOf(el) {
    var l = (el && el.getAttribute("data-lang")) || d.documentElement.lang || "es";
    return l.toLowerCase().indexOf("en") === 0 ? "en" : "es";
  }
  function load(site, opts) {
    opts = opts || {};
    var lang = opts.lang === "en" ? "en" : "es";
    var key = site + "|" + lang;
    if (!cache[key]) {
      var url = (opts.endpoint || ENDPOINT) + "?site=" + encodeURIComponent(site) + "&lang=" + lang;
      cache[key] = fetch(url, { credentials: "omit", mode: "cors" }).then(function (r) {
        if (!r.ok) throw new Error("oneworld-embed " + r.status);
        return r.json();
      }).catch(function (e) { delete cache[key]; throw e; });
    }
    return cache[key];
  }

  /* ── helpers (exported for custom renderers) ───────────────────────────────────────────────── */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function safeUrl(u) { return typeof u === "string" && /^https:\/\/[^\s"'<>]+$/i.test(u) ? u : ""; }
  function t(lang, en, es) { return lang === "en" ? en : es; }
  function parts(iso, tz, lang) {
    var dt = new Date(iso), loc = lang === "en" ? "en-US" : "es-CO", o = {};
    function f(opt) { try { return new Intl.DateTimeFormat(loc, Object.assign({ timeZone: tz || undefined }, opt)).format(dt); } catch (e) { return new Intl.DateTimeFormat(loc, opt).format(dt); } }
    o.weekday = f({ weekday: "short" }).replace(".", "");
    o.day = f({ day: "numeric" });
    o.month = f({ month: "short" }).replace(".", "");
    o.year = f({ year: "numeric" });
    o.time = f({ hour: "numeric", minute: "2-digit" });
    o.long = f({ weekday: "long", day: "numeric", month: "long" });
    return o;
  }
  function price(ev, lang) {
    if (ev.free || !ev.price_from) return t(lang, "Free", "Gratis");
    var n = Number(ev.price_from), c = ev.currency || "USD";
    try {
      return new Intl.NumberFormat(lang === "en" ? "en-US" : "es-CO",
        { style: "currency", currency: c, currencyDisplay: c === "USD" ? "symbol" : "code", maximumFractionDigits: 0 }).format(n);
    } catch (e) { return c + " " + Math.round(n); }
  }
  function actionLabel(ev, lang) {
    if (ev.spots_left === 0) return t(lang, "Sold out", "Agotado");
    return ev.action === "apply" ? t(lang, "Apply", "Aplicar")
      : ev.action === "rsvp" ? t(lang, "Reserve a spot", "Reservar cupo") : t(lang, "Get tickets", "Comprar entrada");
  }
  /** Google-style yellow stars with partial fill (Lee, 16 Oct 2026). */
  function stars(rating, label) {
    var pct = Math.max(0, Math.min(100, (Number(rating) || 0) / 5 * 100));
    return '<span class="owe-stars" role="img" aria-label="' + esc(label || (rating + " / 5")) + '">' +
      '<span class="owe-stars-bg">★★★★★</span><span class="owe-stars-fg" style="width:' + pct.toFixed(0) + '%">★★★★★</span></span>';
  }
  var GOOGLE_G = '<svg class="owe-g" viewBox="0 0 48 48" aria-hidden="true" width="16" height="16"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.6 5.4 2.7 13.3l7.9 6.1C12.5 13.6 17.8 9.5 24 9.5z"/><path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.7c4.3-4 6.9-9.9 6.9-17.1z"/><path fill="#FBBC05" d="M10.6 28.6c-.5-1.4-.8-3-.8-4.6s.3-3.2.8-4.6l-7.9-6.1C1 16.6 0 20.2 0 24s1 7.4 2.7 10.7l7.9-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.7c-2.1 1.4-4.8 2.3-8.5 2.3-6.2 0-11.5-4.1-13.4-9.9l-7.9 6.1C6.6 42.6 14.6 48 24 48z"/></svg>';
  /** Required Google credit: logo + "Google" wording. */
  function googleMark() { return '<span class="owe-google">' + GOOGLE_G + '<span>Google</span></span>'; }

  /** All reviews in one list: One World first (newest), then Google, each with its source. */
  function allReviews(data) {
    var out = [];
    (data.reviews && data.reviews.items || []).forEach(function (r) {
      out.push({ source: "oneworld", author: r.author, author_url: "", author_photo: safeUrl(r.author_photo), rating: r.rating, text: r.text, when: r.created_at, url: "" });
    });
    (data.google && data.google.reviews || []).forEach(function (r) {
      out.push({ source: "google", author: r.author, author_url: safeUrl(r.author_url), author_photo: safeUrl(r.author_photo), rating: r.rating, text: r.text, when: r.when, url: safeUrl(r.url) });
    });
    return out;
  }

  /* ── default renderers ─────────────────────────────────────────────────────────────────────── */
  function css() {
    if (d.getElementById("owe-css")) return;
    var s = d.createElement("style"); s.id = "owe-css";
    s.textContent =
      ":where(.owe){--owe-accent:#2BB3A3;--owe-card:#fff;--owe-ink:inherit;--owe-radius:18px;--owe-shadow:0 8px 30px rgba(0,0,0,.08);font:inherit;color:var(--owe-ink)}" +
      ".owe *{box-sizing:border-box}" +
      ".owe-grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr))}" +
      ".owe-card{display:flex;flex-direction:column;background:var(--owe-card);border-radius:var(--owe-radius);box-shadow:var(--owe-shadow);overflow:hidden;color:inherit;text-decoration:none}" +
      ".owe-img{aspect-ratio:16/10;background:#eee center/cover no-repeat;position:relative}" +
      ".owe-date{position:absolute;left:12px;top:12px;background:rgba(255,255,255,.88);border-radius:12px;padding:6px 10px;text-align:center;line-height:1.1}" +
      ".owe-date b{display:block;font-size:1.4em}.owe-date small{font-size:.7em;letter-spacing:.08em;text-transform:uppercase}" +
      ".owe-body{padding:16px 18px 18px;display:flex;flex-direction:column;gap:6px;flex:1}" +
      ".owe-title{margin:0;font-size:1.1em;line-height:1.25}.owe-meta{opacity:.75;font-size:.9em;margin:0}" +
      ".owe-foot{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:auto;padding-top:12px;border-top:1px solid rgba(0,0,0,.08)}" +
      ".owe-btn{display:inline-block;padding:9px 16px;border-radius:999px;background:var(--owe-accent);color:#fff;font-weight:600;font-size:.9em;white-space:nowrap}" +
      ".owe-empty{padding:22px;border-radius:var(--owe-radius);background:var(--owe-card);box-shadow:var(--owe-shadow);text-align:center}" +
      ".owe-stars{position:relative;display:inline-block;line-height:1;letter-spacing:2px;color:rgba(0,0,0,.18)}" +
      ".owe-stars-fg{position:absolute;inset:0 auto 0 0;overflow:hidden;white-space:nowrap;color:#FBBC04}" +
      ".owe-sum{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin-bottom:16px}.owe-avg{font-size:2em;font-weight:600;line-height:1}" +
      ".owe-rev{background:var(--owe-card);border-radius:var(--owe-radius);box-shadow:var(--owe-shadow);padding:18px;display:flex;flex-direction:column;gap:10px;margin:0}" +
      ".owe-rev blockquote{margin:0;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}" +
      ".owe-who{display:flex;align-items:center;gap:10px;margin-top:auto}.owe-av{width:36px;height:36px;border-radius:50%;background:#ddd center/cover;display:grid;place-items:center;font-weight:600;flex-shrink:0}" +
      ".owe-src{font-size:.78em;opacity:.75;display:inline-flex;align-items:center;gap:4px}.owe-src a{color:inherit}" +
      ".owe-google{display:inline-flex;align-items:center;gap:4px;font-weight:600}.owe-g{flex-shrink:0}" +
      ".owe-links{display:flex;flex-wrap:wrap;gap:12px;margin-top:14px;font-size:.9em}.owe-links a{color:var(--owe-accent);font-weight:600}" +
      ".owe-who a{color:inherit}.owe-section+.owe-section{margin-top:28px;padding-top:24px;border-top:1px solid rgba(0,0,0,.12)}" +
      ".owe-srcname{font-weight:700;font-size:1.05em;display:inline-flex;align-items:center}.owe-srcname .owe-g{width:20px;height:20px}" +
      ".owe-section .owe-avg{font-size:1.5em}.owe-count{opacity:.75}.owe-empty a{color:var(--owe-accent);font-weight:600}";
    d.head.appendChild(s);
  }

  function renderEvents(el, data, lang) {
    var ev = data.events || { upcoming: [], past: [] }, tz = el.getAttribute("data-tz") || "";
    var limit = parseInt(el.getAttribute("data-limit") || "6", 10) || 6;
    var up = (ev.upcoming || []).slice(0, limit);
    var html = up.length ? '<div class="owe-grid">' + up.map(function (e) {
      var p = parts(e.starts_at, e.timezone || tz, lang), img = safeUrl(e.image), href = safeUrl(e.action_url) || safeUrl(e.url);
      var where = e.online ? t(lang, "Online", "En línea") : (e.venue || "");
      var spots = e.spots_left != null ? '<br><small>' + esc(e.spots_left === 0 ? t(lang, "Sold out", "Agotado") : e.spots_left + " " + t(lang, "spots left", "cupos")) + '</small>' : "";
      return '<a class="owe-card" href="' + esc(href) + '" target="_blank" rel="noopener">' +
        '<div class="owe-img"' + (img ? ' style="background-image:url(&quot;' + esc(img) + '&quot;)"' : "") + '>' +
        '<div class="owe-date"><small>' + esc(p.weekday) + '</small><b>' + esc(p.day) + '</b><small>' + esc(p.month) + '</small></div></div>' +
        '<div class="owe-body"><h3 class="owe-title">' + esc(e.title) + '</h3><p class="owe-meta">' + esc(p.time + (where ? " · " + where : "")) + '</p>' +
        (e.description ? '<p class="owe-meta">' + esc(e.description) + '</p>' : "") +
        '<div class="owe-foot"><div><b>' + esc(price(e, lang)) + '</b>' + spots + '</div><span class="owe-btn">' + esc(actionLabel(e, lang)) + '</span></div></div></a>';
    }).join("") + '</div>' : '<p class="owe-empty">' + esc(t(lang, "New events coming soon.", "Pronto habrá nuevos eventos.")) + '</p>';
    var prof = safeUrl(data.member && data.member.profile_url);
    if (prof) html += '<div class="owe-links"><a href="' + esc(prof) + '" target="_blank" rel="noopener">' + esc(t(lang, "See all events on One World →", "Ver todos los eventos en One World →")) + '</a></div>';
    el.innerHTML = html;
  }

  /** One source's header line: "One World 4.8 ★★★★★ (12)" or, for Google, the Google logo in place of the name. */
  function sourceHead(name, avg, count, lang) {
    var label = (name.indexOf("<") >= 0 ? "Google" : name) + " " + Number(avg).toFixed(1) + " / 5, " + count + " " + t(lang, count === 1 ? "review" : "reviews", count === 1 ? "reseña" : "reseñas");
    return '<div class="owe-sum" aria-label="' + esc(label) + '"><span class="owe-srcname">' + name + '</span>' +
      '<span class="owe-avg">' + esc(Number(avg).toFixed(1)) + '</span>' + stars(avg) + '<span class="owe-count">(' + esc(count) + ')</span></div>';
  }
  function reviewCard(r, lang) {
    var av = r.author_photo ? '<span class="owe-av" style="background-image:url(&quot;' + esc(r.author_photo) + '&quot;)"></span>'
      : '<span class="owe-av">' + esc((r.author || "·").charAt(0)) + '</span>';
    var name = r.author_url ? '<a href="' + esc(r.author_url) + '" target="_blank" rel="noopener">' + esc(r.author) + '</a>' : esc(r.author);
    var meta = r.source === "google"
      ? '<span class="owe-src">' + (r.when ? esc(r.when) : "") + (r.url ? (r.when ? " · " : "") + '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(t(lang, "View on Google Maps", "Ver en Google Maps")) + '</a>' : "") + '</span>'
      : "";
    return '<figure class="owe-rev">' + stars(r.rating) + '<blockquote>' + esc(r.text) + '</blockquote>' +
      '<figcaption class="owe-who">' + av + '<div><b>' + name + '</b>' + (meta ? '<br>' + meta : "") + '</div></figcaption></figure>';
  }

  /** Two separate blocks — One World, then Google — never one blended number (Google Places policy:
   *  Google content stays visually separate and is not credited with non-Google content).
   *  A source with no reviews is hidden. data.summary is still sent by the server for older custom pages. */
  function renderReviews(el, data, lang) {
    var all = allReviews(data), g = data.google, ow = data.reviews || {};
    var limit = parseInt(el.getAttribute("data-limit") || "6", 10) || 6;
    var owList = all.filter(function (r) { return r.source === "oneworld"; });
    var gList = all.filter(function (r) { return r.source === "google"; });
    var owCount = Number(ow.count) || 0;
    var gOn = !!(g && g.available && g.rating != null && (Number(g.count) || 0) > 0);
    var gWrite = g && safeUrl(g.write_review_url), gAll = g && safeUrl(g.url);
    var html = "";
    if (owCount && owList.length) {
      html += '<section class="owe-section owe-section-ow" aria-label="One World">' +
        sourceHead("One World", ow.average, owCount, lang) +
        '<div class="owe-grid">' + owList.slice(0, limit).map(function (r) { return reviewCard(r, lang); }).join("") + '</div></section>';
    }
    if (gOn) {
      var links = [];
      if (gWrite) links.push('<a href="' + esc(gWrite) + '" target="_blank" rel="noopener">' + esc(t(lang, "Write a review on Google", "Escribe una reseña en Google")) + '</a>');
      if (gAll) links.push('<a href="' + esc(gAll) + '" target="_blank" rel="noopener">' + esc(t(lang, "All Google reviews", "Todas las reseñas en Google")) + '</a>');
      html += '<section class="owe-section owe-section-google" aria-label="Google">' +
        sourceHead(googleMark(), g.rating, Number(g.count) || 0, lang) +
        (gList.length ? '<div class="owe-grid">' + gList.slice(0, limit).map(function (r) { return reviewCard(r, lang); }).join("") + '</div>' : "") +
        (links.length ? '<div class="owe-links">' + links.join("") + '</div>' : "") + '</section>';
    }
    if (!html) {
      html = '<p class="owe-empty">' + esc(t(lang, "No reviews yet", "Aún no hay reseñas")) +
        (gWrite ? '<br><a href="' + esc(gWrite) + '" target="_blank" rel="noopener">' + esc(t(lang, "Write a review on Google", "Escribe una reseña en Google")) + '</a>' : "") + '</p>';
    }
    el.innerHTML = html;
  }

  function mount(el) {
    var site = el.getAttribute("data-oneworld-events") || el.getAttribute("data-oneworld-reviews");
    if (!site) return;
    var lang = langOf(el);
    el.classList.add("owe");
    el.setAttribute("aria-busy", "true");
    load(site, { lang: lang }).then(function (data) {
      if (el.hasAttribute("data-oneworld-events")) renderEvents(el, data, lang); else renderReviews(el, data, lang);
    }).catch(function () {
      el.innerHTML = "";              // fail quiet: never a broken card on someone's website
    }).then(function () { el.removeAttribute("aria-busy"); });
  }
  function mountAll() {
    css();
    var els = d.querySelectorAll("[data-oneworld-events],[data-oneworld-reviews]");
    for (var i = 0; i < els.length; i++) mount(els[i]);
  }

  w.OneWorldEmbed = {
    version: "1.1.0",
    load: load,
    mountAll: mountAll,
    helpers: { esc: esc, reviewCard: reviewCard, sourceHead: sourceHead, safeUrl: safeUrl, parts: parts, price: price, actionLabel: actionLabel, stars: stars, googleMark: googleMark, allReviews: allReviews },
  };
  if (d.readyState === "loading") d.addEventListener("DOMContentLoaded", mountAll); else mountAll();
  // Re-render when the site switches language (<html lang> changes).
  if (w.MutationObserver) new MutationObserver(function () {
    var els = d.querySelectorAll("[data-oneworld-events]:not([data-lang]),[data-oneworld-reviews]:not([data-lang])");
    for (var i = 0; i < els.length; i++) mount(els[i]);
  }).observe(d.documentElement, { attributes: true, attributeFilter: ["lang"] });
})(window, document);
