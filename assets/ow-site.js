/* One World website runtime — language, One ID state, contact form.
   Built by PUB30 for the 2026 site redesign. One file, no framework, no CDN.

   LANGUAGES: English ships inside the HTML. Every other language is one JSON file in
   /assets/i18n/<code>.json keyed by the data-i18n ids the build stamps on each block of text.
   To add a language: add its JSON file, then add it to LANGS below. Nothing else changes.
   The preference is shared with the rest of the site through localStorage 'owl-lang', and
   ?owl_lang=<code> in the address wins, exactly as on the previous homepage. */
(function () {
  'use strict';
  var ROOT = document.documentElement;
  var P = ROOT.getAttribute('data-ow-prefix') || '';
  var V = ROOT.getAttribute('data-ow-v') || '1';

  var LANGS = [
    { k: 'en', label: 'USA', short: 'EN', html: 'en', flag: 'us' },
    { k: 'co', label: 'Colombia', short: 'CO', html: 'es-CO', flag: 'co' },
    { k: 'es', label: 'España', short: 'ES', html: 'es-ES', flag: 'es' },
    { k: 'de', label: 'Deutschland', short: 'DE', html: 'de-DE', flag: 'de' },
    { k: 'ru', label: 'Россия', short: 'RU', html: 'ru-RU', flag: 'ru' },
    { k: 'zh', label: '中国', short: 'ZH', html: 'zh-CN', flag: 'cn' },
    { k: 'pt', label: 'Brasil', short: 'PT', html: 'pt-BR', flag: 'br' }
  ];
  /* A saved language this build does not carry yet falls back to its nearest neighbour. */
  var FALLBACK = {};

  var FLAGS = {
    us: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="14" fill="#B22234"/><path d="M0 1.6h20M0 4.3h20M0 7h20M0 9.7h20M0 12.4h20" stroke="#fff" stroke-width="1.08"/><rect width="8.6" height="7.5" fill="#3C3B6E"/></svg>',
    co: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="7" fill="#FCD116"/><rect y="7" width="20" height="3.5" fill="#003893"/><rect y="10.5" width="20" height="3.5" fill="#CE1126"/></svg>',
    es: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="14" fill="#AA151B"/><rect y="3.5" width="20" height="7" fill="#F1BF00"/></svg>',
    de: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="4.67" fill="#000"/><rect y="4.67" width="20" height="4.67" fill="#DD0000"/><rect y="9.33" width="20" height="4.67" fill="#FFCE00"/></svg>',
    ru: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="4.67" fill="#fff"/><rect y="4.67" width="20" height="4.67" fill="#0039A6"/><rect y="9.33" width="20" height="4.67" fill="#D52B1E"/></svg>',
    cn: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="14" fill="#DE2910"/><path d="M4 2.2l.7 2.1H7L5.2 5.6l.7 2.1L4 6.4 2.1 7.7l.7-2.1L1 4.3h2.3z" fill="#FFDE00"/></svg>',
    br: '<svg class="ow-flag" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="14" fill="#009C3B"/><path d="M10 1.5 18 7l-8 5.5L2 7z" fill="#FFDF00"/><circle cx="10" cy="7" r="3" fill="#002776"/></svg>'
  };

  var UI_EN = {
    'ui.signin': 'Sign in', 'ui.signin_long': 'Sign in with One ID', 'ui.open': 'Open my apps',
    'ui.signout': 'Sign out', 'ui.hi': 'Hi, {name}', 'ui.signed_in': 'Signed in', 'ui.lang': 'Language and country',
    'ui.account': 'Your One ID', 'ui.signout_local': 'Signed out on this device. We could not confirm the sign-out on your other devices.', 'ui.required': 'Please fill in this field.', 'ui.email_bad': 'Enter a valid email address.'
  };

  function find(k) { for (var i = 0; i < LANGS.length; i++) if (LANGS[i].k === k) return LANGS[i]; return null; }
  function store(k) { try { localStorage.setItem('owl-lang', k); } catch (e) {} }
  function initialLang() {
    var q = null;
    try { q = new URLSearchParams(location.search).get('owl_lang'); } catch (e) {}
    var s = null;
    try { s = localStorage.getItem('owl-lang'); } catch (e) {}
    function norm(v) { if (!v) return null; if (!find(v) && FALLBACK[v]) v = FALLBACK[v]; return find(v) ? v : null; }
    var fromQuery = norm(q);
    if (fromQuery) { store(fromQuery); return fromQuery; }   /* a valid ?owl_lang is a choice: keep it on the next page */
    return norm(s) || 'en';                                  /* an invalid one is ignored, never a reset */
  }

  /* ---------------- translation engine ---------------- */
  var dicts = {};
  var origText = new WeakMap();
  var origAttr = new WeakMap();
  var current = 'en';

  function load(k) {
    if (k === 'en') return Promise.resolve({});
    if (dicts[k]) return Promise.resolve(dicts[k]);
    return fetch(P + '/assets/i18n/' + k + '.json?v=' + V, { credentials: 'omit' })
      .then(function (r) { if (!r.ok) throw new Error('i18n ' + r.status); return r.json(); })
      .then(function (d) { dicts[k] = d; return d; });
  }
  function dec(s) { return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&'); }

  /* Templates carry the block's own tags as numbered placeholders (<0>…</0>, <1/>), numbered in
     document order. Rebuilding from the ORIGINAL element keeps every href, class and icon. */
  function rebuild(el, tpl) {
    var orig = origText.get(el);
    if (!orig) { orig = el.cloneNode(true); origText.set(el, orig); }
    var els = orig.querySelectorAll('*');
    var frag = document.createDocumentFragment();
    var stack = [frag];
    var re = /<(\d+)\/>|<(\d+)>|<\/(\d+)>|([^<]+)/g, m;
    while ((m = re.exec(tpl))) {
      var top = stack[stack.length - 1];
      if (m[1] != null) { if (!els[+m[1]]) throw new Error('slot'); top.appendChild(els[+m[1]].cloneNode(true)); }
      else if (m[2] != null) { if (!els[+m[2]]) throw new Error('slot'); var c = els[+m[2]].cloneNode(false); top.appendChild(c); stack.push(c); }
      else if (m[3] != null) { if (stack.length > 1) stack.pop(); }
      else top.appendChild(document.createTextNode(dec(m[4])));
    }
    while (el.firstChild) el.removeChild(el.firstChild);
    el.appendChild(frag);
  }
  function restore(el) {
    var orig = origText.get(el);
    if (!orig) return;
    var c = orig.cloneNode(true);
    while (el.firstChild) el.removeChild(el.firstChild);
    while (c.firstChild) el.appendChild(c.firstChild);
  }

  function applyDict(k, d) {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var t = k === 'en' ? null : d[el.getAttribute('data-i18n')];
      try { if (t) rebuild(el, t); else restore(el); } catch (e) { restore(el); }
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      var saved = origAttr.get(el);
      if (!saved) { saved = {}; origAttr.set(el, saved); }
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var i = pair.indexOf(':'); if (i < 1) return;
        var a = pair.slice(0, i), id = pair.slice(i + 1);
        if (!(a in saved)) saved[a] = el.getAttribute(a);
        var t = k === 'en' ? null : d[id];
        el.setAttribute(a, t ? dec(t) : saved[a]);
      });
    });
    var L = find(k);
    ROOT.setAttribute('lang', L ? L.html : 'en');
    current = k;
    window.OWL_LANG = k;
    renderLangButton();
    renderAccount();
    if (window.owRelabel) window.owRelabel();
    fitHeadings();
    document.querySelectorAll('[data-contact-form] input,[data-contact-form] textarea').forEach(function (f) { f.setCustomValidity(''); });
    try { document.dispatchEvent(new CustomEvent('ow:lang', { detail: k })); } catch (e) {}
  }
  /* A long word (Russian "Повседневная", German compounds) must not be split mid-word in a big
     heading: shrink that heading just enough for its longest word to fit (never below 72%). */
  function fitHeadings() {
    document.querySelectorAll('main h1, main h2, main h3').forEach(function (h) {
      h.style.fontSize = '';
      if (current === 'en') return;
      var base = parseFloat(getComputedStyle(h).fontSize), size = base;
      /* the space the heading really has: its column, which a long word may already have widened */
      var left = h.getBoundingClientRect().left, avail = Math.min(h.clientWidth, document.documentElement.clientWidth - 2 * Math.max(left, 0));
      if (!(avail > 0)) return;
      h.style.overflowWrap = 'normal'; h.style.hyphens = 'manual'; h.style.width = avail + 'px';
      var floor = base * 0.72;
      while (h.scrollWidth > avail + 1 && size > floor) { size = Math.max(floor, size - base * 0.04); h.style.fontSize = size + 'px'; }
      h.style.overflowWrap = ''; h.style.hyphens = ''; h.style.width = '';
    });
  }
  var fitTimer;
  window.addEventListener('resize', function () { clearTimeout(fitTimer); fitTimer = setTimeout(fitHeadings, 150); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fitHeadings(); });

  function ui(key) {
    var d = dicts[current];
    return (current !== 'en' && d && d[key]) || UI_EN[key] || key;
  }
  var langSeq = 0;
  function setLang(k, save) {
    if (!find(k)) k = 'en';
    if (save) store(k);
    var mine = ++langSeq;   /* a slower earlier request must never overwrite the newest choice */
    return load(k).then(function (d) { if (mine === langSeq) applyDict(k, d); },
      function () { if (mine === langSeq) applyDict('en', {}); })
      .then(function () { if (mine === langSeq) ROOT.classList.remove('ow-i18n-pending'); });
  }

  /* ---------------- menus ---------------- */
  var openMenu = null;
  function closeMenus() {
    if (!openMenu) return;
    openMenu.menu.hidden = true;
    openMenu.btn.setAttribute('aria-expanded', 'false');
    openMenu = null;
  }
  function wireMenu(btn, menu) {
    if (!btn || !menu) return;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var was = openMenu && openMenu.menu === menu;
      closeMenus();
      if (was) return;
      menu.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
      openMenu = { btn: btn, menu: menu };
      var first = menu.querySelector('button,a');
      if (first && e.detail === 0) first.focus();
    });
    menu.addEventListener('click', function (e) { e.stopPropagation(); });
    menu.addEventListener('keydown', function (e) {
      var items = Array.prototype.slice.call(menu.querySelectorAll('button,a'));
      var i = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); (items[i + 1] || items[0]).focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); (items[i - 1] || items[items.length - 1]).focus(); }
    });
  }
  document.addEventListener('click', closeMenus);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && openMenu) { var b = openMenu.btn; closeMenus(); b.focus(); }
  });

  /* ---------------- language switcher ---------------- */
  var langBtn = document.getElementById('ow-lang-btn');
  var langMenu = document.getElementById('ow-lang-menu');
  function renderLangButton() {
    if (!langBtn) return;
    var L = find(current) || LANGS[0];
    langBtn.innerHTML = FLAGS[L.flag] + '<span class="ow-code">' + L.short + '</span>';
    langBtn.setAttribute('aria-label', ui('ui.lang') + ': ' + L.label);
    if (langMenu) langMenu.setAttribute('aria-label', ui('ui.lang'));
    if (langMenu) langMenu.querySelectorAll('[data-lang]').forEach(function (b) {
      var on = b.getAttribute('data-lang') === current;
      b.classList.toggle('on', on);
      b.setAttribute('aria-checked', on ? 'true' : 'false');
    });
  }
  if (langMenu) {
    langMenu.innerHTML = LANGS.map(function (L) {
      return '<button type="button" role="menuitemradio" data-lang="' + L.k + '">' + FLAGS[L.flag] + '<span>' + L.label + '</span></button>';
    }).join('');
    langMenu.addEventListener('click', function (e) {
      var b = e.target.closest('[data-lang]');
      if (!b) return;
      closeMenus();
      setLang(b.getAttribute('data-lang'), true);
      langBtn.focus();
    });
  }
  wireMenu(langBtn, langMenu);

  /* ---------------- One ID state ----------------
     The session is written by the One World app (app.oneworldlabs.ai) and shared across
     *.oneworldlabs.ai through the parent-domain cookie; /assets/oneid-bridge.js copies it into
     this page's storage before this file runs. This file only READS it — it never mints or
     refreshes a token. */
  var SB_URL = 'https://wseblryyqxawvbjmylbo.supabase.co';
  var SB_ANON = 'sb_publishable_hO1MOsFr6lk0XDC6gizF8g_WfBZ68Tc';
  var KEY = 'sb-wseblryyqxawvbjmylbo-auth-token';
  /* Shown as signed in ONLY for a well-formed, unexpired session. Both copies are read (this
     page's storage and the shared parent-domain cookie the app writes) and the fresher one wins;
     nothing is written back here. An expired or unknown session shows "Sign in" — opening the
     app refreshes it. Display only: this is never used to authorise anything. */
  function shape(raw) {
    try {
      var s = JSON.parse(raw || 'null');
      if (s && s.currentSession) s = s.currentSession;
      if (!s || typeof s.access_token !== 'string' || !s.access_token || typeof s.refresh_token !== 'string' || !s.refresh_token) return null;
      if (!s.user || typeof s.user.id !== 'string' || !s.user.id) return null;
      if (typeof s.expires_at !== 'number' || !isFinite(s.expires_at)) return null;
      return s;
    } catch (e) { return null; }
  }
  function cookieRaw() {
    try {
      var jar = {}; document.cookie.split('; ').forEach(function (p) { var i = p.indexOf('='); if (i > 0) jar[decodeURIComponent(p.slice(0, i))] = decodeURIComponent(p.slice(i + 1)); });
      if (jar[KEY] != null) return jar[KEY];
      var out = ''; for (var n = 0; n < 24 && jar[KEY + '.' + n] != null; n++) out += jar[KEY + '.' + n];
      return out || null;
    } catch (e) { return null; }
  }
  function session() {
    var a = null, b = shape(cookieRaw());
    try { a = shape(localStorage.getItem(KEY)); } catch (e) {}
    var s = a && b ? (b.expires_at > a.expires_at ? b : a) : (a || b);
    return s && s.expires_at * 1000 > Date.now() ? s : null;
  }
  function displayName(u) {
    var m = (u && u.user_metadata) || {};
    var n = m.full_name || m.name || (u && u.email) || '';
    return String(n).split(' ')[0].split('@')[0];
  }
  /* VAIA gets only what it needs to call its endpoint: who, and the short-lived access token.
     Never the refresh token, never the whole stored session. */
  window.OW_SESSION = function () {
    var s = session();
    return s ? { userId: s.user.id, accessToken: s.access_token } : null;
  };
  var acctIn = document.getElementById('ow-acct-in');
  var acctOut = document.getElementById('ow-acct-out');
  var acctBtn = document.getElementById('ow-acct-btn');
  var acctMenu = document.getElementById('ow-acct-menu');
  /* Tell the page (VAIA) that the sign-in state may have changed: this-tab sign-out, other tabs, shared cookie. */
  function announceSession() { try { document.dispatchEvent(new CustomEvent('ow:session')); } catch (e) {} }
  function renderAccount() {
    announceSession();
    if (!acctIn || !acctOut) return;
    var s = session();
    var outLong = acctOut.querySelector('.ow-long'), outShort = acctOut.querySelector('.ow-short');
    if (outLong) outLong.textContent = ui('ui.signin_long');
    if (outShort) outShort.textContent = ui('ui.signin');
    if (!s) { acctIn.hidden = true; acctOut.hidden = false; closeMenus(); return; }
    var u = s.user || {};
    var name = displayName(u);
    var pic = u.user_metadata && (u.user_metadata.avatar_url || u.user_metadata.picture);
    acctBtn.textContent = '';
    if (pic && /^https:\/\//.test(pic)) {
      var img = document.createElement('img');
      img.src = pic; img.alt = ''; img.referrerPolicy = 'no-referrer';
      img.onerror = function () { acctBtn.textContent = (name || '?').charAt(0).toUpperCase(); };
      acctBtn.appendChild(img);
    } else acctBtn.textContent = (name || '?').charAt(0).toUpperCase();
    acctBtn.setAttribute('aria-label', ui('ui.account') + (name ? ': ' + name : ''));
    var who = acctMenu.querySelector('.ow-who strong'), mail = acctMenu.querySelector('.ow-who span');
    who.textContent = name ? ui('ui.hi').replace('{name}', name) : ui('ui.signed_in');
    mail.textContent = u.email || 'One ID';
    acctMenu.querySelector('.ow-open span').textContent = ui('ui.open');
    acctMenu.querySelector('.ow-signout span').textContent = ui('ui.signout');
    acctOut.hidden = true; acctIn.hidden = false;
  }
  function clearSharedCookie() {
    var base = '=; Domain=.oneworldlabs.ai; Path=/; Max-Age=0; SameSite=Lax';
    document.cookie = encodeURIComponent(KEY) + base;
    for (var i = 0; i < 24; i++) document.cookie = encodeURIComponent(KEY + '.' + i) + base;
  }
  var signingOut = false;
  function notice(text) {
    var n = document.getElementById('ow-notice');
    if (!n) { n = document.createElement('div'); n.id = 'ow-notice'; n.setAttribute('role', 'status'); document.body.appendChild(n); }
    n.textContent = text; n.hidden = false;
    clearTimeout(notice.t); notice.t = setTimeout(function () { n.hidden = true; }, 7000);
  }
  function signOut() {
    if (signingOut) return;
    signingOut = true;
    var s = session();
    /* This device is always signed out. "Everywhere" is only claimed when the server confirms it. */
    var finish = function (everywhere) {
      try { localStorage.removeItem(KEY); } catch (e) {}
      try { sessionStorage.removeItem('ow_bridge_had_session'); } catch (e) {}
      clearSharedCookie();
      signingOut = false;
      renderAccount();
      if (!everywhere) notice(ui('ui.signout_local'));
    };
    if (!s) return finish(true);   /* nothing to revoke here; no claim is made */
    /* Exactly one outcome: the first of server answer / network error / 6 s deadline wins; a late
       answer is ignored. Only a 2xx counts as confirmed everywhere — anything else, including
       401, is reported as this-device-only. */
    var settled = false;
    var once = function (everywhere) { if (settled) return; settled = true; clearTimeout(timer); finish(everywhere); };
    var ctl = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) { try { ctl.abort(); } catch (e) {} } once(false); }, 6000);
    try {
      fetch(SB_URL + '/auth/v1/logout?scope=global', {
        method: 'POST', signal: ctl ? ctl.signal : undefined,
        headers: { apikey: SB_ANON, Authorization: 'Bearer ' + s.access_token }
      }).then(function (r) { once(!!(r && r.ok)); }, function () { once(false); });
    } catch (e) { once(false); }
  }
  wireMenu(acctBtn, acctMenu);
  if (acctMenu) acctMenu.querySelector('.ow-signout').addEventListener('click', function () { closeMenus(); signOut(); });
  window.addEventListener('storage', function (e) { if (!e.key || e.key === KEY) renderAccount(); });
  window.addEventListener('focus', renderAccount);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) renderAccount(); });

  /* ---------------- contact form (mailto, same as the previous homepage) ---------------- */
  var form = document.querySelector('[data-contact-form]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = new FormData(form);
      var g = function (k) { return (d.get(k) || '').toString().trim(); };
      var topic = g('topic');
      var subject = encodeURIComponent('One World Labs inquiry' + (topic ? ' — ' + topic : ''));
      var body = encodeURIComponent(['Name: ' + g('name'), 'Email: ' + g('email'), 'Phone: ' + (g('phone') || 'Not provided'),
        'Topic: ' + topic, 'Language: ' + current, '', g('message')].join('\n'));
      location.href = 'mailto:support@oneworldlabs.ai?subject=' + subject + '&body=' + body;
    });
    form.querySelectorAll('input,textarea').forEach(function (el) {
      el.addEventListener('input', function () { el.setCustomValidity(''); });
      el.addEventListener('invalid', function () {
        el.setCustomValidity('');
        if (current === 'en') return;
        if (el.validity.valueMissing) el.setCustomValidity(ui('ui.required'));
        else if (el.validity.typeMismatch && el.type === 'email') el.setCustomValidity(ui('ui.email_bad'));
      });
    });
  }

  /* ---------------- start ---------------- */
  current = 'en';
  renderAccount();
  setLang(initialLang(), false);
})();
