/* One World website v2 (13 Nov 2026): phone previews, the "What are you looking for?" explorer,
   one app card at a time, the two-sided app pages and the blog filters. No framework.
   Every piece works without this file: lists stay visible and links still go somewhere. */
(function () {
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function nearest(track, items) {
    var c = track.scrollLeft + track.clientWidth / 2, best = 0, d = 1e9;
    items.forEach(function (el, i) { var m = el.offsetLeft + el.offsetWidth / 2, x = Math.abs(m - c); if (x < d) { d = x; best = i; } });
    return best;
  }
  function centre(track, el, smooth) {
    var left = el.offsetLeft - (track.clientWidth - el.offsetWidth) / 2;
    track.scrollTo({ left: left, behavior: smooth && !reduce ? 'smooth' : 'auto' });
  }

  /* ── phone previews: one app in focus; neighbours dimmed ─────────────── */
  $$('[data-screens]').forEach(function (stage) {
    var track = $('.screens', stage), slides = $$('.slide', track), box = stage.closest('.apps2') || stage;
    var count = $('.oc-count', box), prev = $('[data-prev]', box), next = $('[data-next]', box);
    var at = -1, timer = null, touched = false, visible = true;
    function mark(i) {
      if (i === at) return; at = i;
      slides.forEach(function (p, k) { var on = k === i; p.classList.toggle('on', on); p.setAttribute('aria-hidden', on ? 'false' : 'true'); $$('a', p).forEach(function (a) { a.tabIndex = on ? 0 : -1; }); });
      if (count) count.textContent = (i + 1) + ' / ' + slides.length;
    }
    var start = +(stage.getAttribute('data-start') || 0);
    requestAnimationFrame(function () { centre(track, slides[start], false); mark(start); });
    var raf = 0;
    track.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(function () { mark(nearest(track, slides)); }); }, { passive: true });
    function go(i) { stop(); i = (i + slides.length) % slides.length; centre(track, slides[i], true); mark(i); }
    if (prev) prev.addEventListener('click', function () { go(at - 1); });
    if (next) next.addEventListener('click', function () { go(at + 1); });
    /* a tap on a dimmed neighbour brings it into focus instead of following its link */
    track.addEventListener('click', function (e) {
      var s = e.target.closest('.slide'); if (!s) return; var k = slides.indexOf(s);
      if (k !== at) { e.preventDefault(); go(k); }
    }, true);
    ['pointerdown', 'touchstart', 'wheel', 'keydown'].forEach(function (e) { track.addEventListener(e, stop, { passive: true }); });
    function stop() { touched = true; clearInterval(timer); }
    if (!reduce && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }, { threshold: .4 }).observe(track);
      timer = setInterval(function () { if (!touched && visible && !document.hidden) { centre(track, slides[(at + 1) % slides.length], true); } }, 4200);
    }
    addEventListener('resize', function () { if (at >= 0) centre(track, slides[at], false); });
  });

  /* ── explorer: category → its choices → the app's own page ─────────── */
  $$('[data-explorer]').forEach(function (ex) {
    ex.classList.add('js');
    var cats = $('.ex-cats', ex), panels = $$('.ex-panel', ex);
    panels.forEach(function (p) { p.hidden = true; });
    function show(id) {
      var p = document.getElementById(id); if (!p) return;
      cats.hidden = true; panels.forEach(function (x) { x.hidden = x !== p; });
      $$('.ex-cat', ex).forEach(function (b) { b.setAttribute('aria-expanded', b.getAttribute('aria-controls') === id ? 'true' : 'false'); });
      var h = $('h3', p); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
      var top = ex.getBoundingClientRect().top; if (top < 0 || top > innerHeight * .25) window.scrollBy({ top: top - 16, behavior: reduce ? 'auto' : 'smooth' });
    }
    function back(from) {
      panels.forEach(function (x) { x.hidden = true; }); cats.hidden = false;
      var b = $('.ex-cat[aria-controls="' + from + '"]', ex); if (b) { b.setAttribute('aria-expanded', 'false'); b.focus(); }
    }
    $$('.ex-cat', ex).forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('aria-controls')); }); });
    $$('.ex-back', ex).forEach(function (b) { b.hidden = false; b.addEventListener('click', function () { back(b.closest('.ex-panel').id); }); });
    ex.addEventListener('keydown', function (e) { if (e.key === 'Escape') { var open = panels.filter(function (p) { return !p.hidden; })[0]; if (open) back(open.id); } });
  });

  /* ── one app at a time ─────────────────────────────────────────────── */
  $$('[data-onecard]').forEach(function (box) {
    var track = $('.oc-track', box), cards = $$('.oc', track), count = $('.oc-count', box), at = 0;
    function set(i) { at = i; if (count) count.textContent = (i + 1) + ' / ' + cards.length; cards.forEach(function (c, k) { c.setAttribute('aria-hidden', k === i ? 'false' : 'true'); c.inert = k !== i; }); }
    function go(i) { i = (i + cards.length) % cards.length; track.scrollTo({ left: cards[i].offsetLeft - track.offsetLeft, behavior: reduce ? 'auto' : 'smooth' }); set(i); }
    var raf = 0;
    track.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(function () { var i = Math.round(track.scrollLeft / track.clientWidth); if (i !== at) set(i); }); }, { passive: true });
    var p = $('[data-prev]', box), n = $('[data-next]', box);
    if (p) p.addEventListener('click', function () { go(at - 1); });
    if (n) n.addEventListener('click', function () { go(at + 1); });
    set(0);
  });

  /* ── app pages: two sides of the marketplace, a toggle and a swipe ─── */
  $$('[data-sides]').forEach(function (wrap) {
    var seg = $('.seg', document), tabs = $$('.seg button', document), track = $('.sides', wrap), panes = $$('.side', track), at = 0;
    function fit() { var h = panes[at].offsetHeight; if (h) track.style.height = h + 'px'; }
    function set(i, push) {
      at = i; seg.setAttribute('data-at', i);
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === i ? 'true' : 'false'); t.tabIndex = k === i ? 0 : -1; });
      panes.forEach(function (p, k) { p.inert = k !== i; p.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      fit();
      if (push) { try { var u = new URL(location.href); u.searchParams.set('side', panes[i].getAttribute('data-side')); history.replaceState(null, '', u); } catch (e) {} }
    }
    function go(i, smooth) {
      track.scrollTo({ left: panes[i].offsetLeft - track.offsetLeft, behavior: smooth && !reduce ? 'smooth' : 'auto' }); set(i, true);
      var top = wrap.getBoundingClientRect().top; if (top < -40) window.scrollBy({ top: top - 90, behavior: reduce ? 'auto' : 'smooth' });
    }
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { go(k, true); });
      t.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { var j = (k + 1) % 2; tabs[j].focus(); go(j, true); e.preventDefault(); } });
    });
    var raf = 0;
    track.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(function () { var i = Math.round(track.scrollLeft / track.clientWidth); if (i !== at && i >= 0 && i < panes.length) set(i, true); }); }, { passive: true });
    var want = 0;
    try { var s = new URLSearchParams(location.search).get('side'); panes.forEach(function (p, k) { if (p.getAttribute('data-side') === s) want = k; }); } catch (e) {}
    requestAnimationFrame(function () { track.scrollLeft = panes[want].offsetLeft - track.offsetLeft; set(want, false); });
    addEventListener('resize', function () { track.scrollLeft = panes[at].offsetLeft - track.offsetLeft; fit(); });
    addEventListener('load', fit);
    if ('ResizeObserver' in window) new ResizeObserver(fit).observe(panes[0]), new ResizeObserver(fit).observe(panes[1]);
    $$('details', track).forEach(function (d) { d.addEventListener('toggle', fit); });
  });

  /* ── OneJob: "?need=cleaning" from the explorer names the job you came for ─ */
  (function () {
    var line = $('[data-need-line]'); if (!line) return;
    var need = null; try { need = new URLSearchParams(location.search).get('need'); } catch (e) {}
    if (!need) return;
    var names = JSON.parse(line.getAttribute('data-names') || '{}');
    if (!names[need]) return;
    $('b', line).textContent = names[need]; line.hidden = false;
    $$('[data-need]').forEach(function (a) { if (a.getAttribute('data-need') === need) a.classList.add('hit'); });
  })();

  /* ── blog: filter by topic, kept in the address so it can be shared ─── */
  $$('[data-filters]').forEach(function (bar) {
    var links = $$('a[data-topic]', bar), cards = $$('[data-topics]'), empty = $('[data-empty]');
    function apply(t, push) {
      var n = 0;
      links.forEach(function (a) { a.setAttribute('aria-current', a.getAttribute('data-topic') === t ? 'true' : 'false'); });
      cards.forEach(function (c) { var ok = t === 'all' || (' ' + c.getAttribute('data-topics') + ' ').indexOf(' ' + t + ' ') >= 0; c.hidden = !ok; if (ok) n++; });
      if (empty) empty.hidden = n > 0;
      if (push) { try { var u = new URL(location.href); if (t === 'all') u.searchParams.delete('topic'); else u.searchParams.set('topic', t); history.replaceState(null, '', u); } catch (e) {} }
    }
    links.forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); apply(a.getAttribute('data-topic'), true); }); });
    var t = 'all'; try { t = new URLSearchParams(location.search).get('topic') || 'all'; } catch (e) {}
    if (!links.some(function (a) { return a.getAttribute('data-topic') === t; })) t = 'all';
    apply(t, false);
  });
})();
