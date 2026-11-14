/* One World background music (Lee, 13 Nov 2026).
   A small round glass button, bottom right and above the chat bubble, turns the music on and off;
   a slider next to it sets the volume. Browsers do not allow sound before the visitor does
   something, so the music starts on the first tap, click or key press, at a low volume. A visitor
   who turns it off stays off (remembered on this device). The track is an original loop made for
   One World (assets/audio/one-world-lounge.mp3), so there is no licence to track.
   Loaded by ow-site.js on every page that uses the shared header. */
(function () {
  'use strict';
  if (window.__owMusic) return;
  window.__owMusic = true;

  var SRC = '/assets/audio/one-world-lounge.mp3?v=1';
  var LOOP = 3681391 / 44100;          /* exact length of the loop in seconds */
  var KEY = 'ow-music', VKEY = 'ow-music-vol', PKEY = 'ow-music-pos';
  var DEF_VOL = 0.25;
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function ssGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }

  var muted = lsGet(KEY) === 'off';
  var vol = parseFloat(lsGet(VKEY));
  if (!(vol >= 0 && vol <= 1)) vol = DEF_VOL;
  var es = /^es/i.test(document.documentElement.lang || '');
  var T = es
    ? { on: 'Activar la música', off: 'Silenciar la música', vol: 'Volumen de la música' }
    : { on: 'Turn music on', off: 'Turn music off', vol: 'Music volume' };

  /* ---------- sound ---------- */
  var AC = window.AudioContext || window.webkitAudioContext;
  var ctx = null, gain = null, buffer = null, source = null, loopStart = 0;
  var startedAt = 0, startOffset = 0, loading = null, playing = false, el = null;

  function position() {
    if (!playing) return startOffset;
    if (el) return el.currentTime;
    return (startOffset + ctx.currentTime - startedAt) % LOOP;
  }
  function savePos() { if (playing) ssSet(PKEY, String(position())); }

  function load() {
    if (loading) return loading;
    if (!AC) {
      el = new Audio(SRC); el.loop = true; el.preload = 'auto';
      loading = Promise.resolve();
      return loading;
    }
    ctx = ctx || new AC();
    gain = ctx.createGain();
    gain.gain.value = 0;
    gain.connect(ctx.destination);
    loading = fetch(SRC, { credentials: 'omit' })
      .then(function (r) { if (!r.ok) throw new Error('music ' + r.status); return r.arrayBuffer(); })
      .then(function (a) { return new Promise(function (ok, no) { ctx.decodeAudioData(a, ok, no); }); })
      .then(function (b) {
        buffer = b;
        /* Some decoders keep the MP3 encoder's silent lead-in: start the loop at the first sound. */
        var d = b.getChannelData(0), i = 0, max = Math.min(d.length, 8192);
        while (i < max && Math.abs(d[i]) < 1e-4) i++;
        loopStart = i < max ? i / b.sampleRate : 0;
      });
    return loading;
  }

  var pending = false;
  function play() {
    if (playing || muted || pending) return;
    pending = true;
    var want = parseFloat(ssGet(PKEY)) || 0;
    var resumed = Promise.resolve();
    if (!ctx && AC) { try { ctx = new AC(); } catch (e) {} }
    if (ctx && ctx.state !== 'running') { try { resumed = ctx.resume() || resumed; } catch (e) {} }
    Promise.all([load(), resumed.catch(function () {})]).then(function () {
      pending = false;
      if (playing || muted) return;
      if (el) {
        el.volume = vol;
        try { el.currentTime = want % LOOP; } catch (e) {}
        var p = el.play();
        playing = true;
        if (p && p.catch) p.catch(function () { playing = false; render(); });
        render();
        return;
      }
      if (ctx.state !== 'running') return;   /* still blocked: the next tap will start it */
      source = ctx.createBufferSource();
      source.buffer = buffer;
      source.loop = true;
      source.loopStart = loopStart;
      source.loopEnd = Math.min(buffer.duration, loopStart + LOOP);
      source.connect(gain);
      startOffset = want % LOOP;
      startedAt = ctx.currentTime;
      source.start(0, loopStart + startOffset);
      gain.gain.cancelScheduledValues(ctx.currentTime);
      gain.gain.setValueAtTime(0, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(vol, ctx.currentTime + 1.5);   /* fade in */
      playing = true;
      render();
    }).catch(function () { pending = false; playing = false; render(); });
  }

  function stop() {
    if (!playing) return;
    savePos();
    startOffset = position();
    playing = false;
    if (el) { el.pause(); }
    else if (source) {
      var s = source; source = null;
      gain.gain.cancelScheduledValues(ctx.currentTime);
      gain.gain.setValueAtTime(gain.gain.value, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.25);
      setTimeout(function () { try { s.stop(); s.disconnect(); } catch (e) {} }, 300);
    }
    render();
  }

  function setVol(v) {
    vol = Math.max(0, Math.min(1, v));
    lsSet(VKEY, String(vol));
    if (el) el.volume = vol;
    else if (gain && playing) { gain.gain.cancelScheduledValues(ctx.currentTime); gain.gain.setTargetAtTime(vol, ctx.currentTime, 0.05); }
  }

  /* ---------- the control ---------- */
  var css = '.ow-music{position:fixed;right:max(20px,env(safe-area-inset-right));bottom:calc(20px + env(safe-area-inset-bottom));z-index:2147482000;display:flex;align-items:center;gap:8px;flex-direction:row-reverse}' +
    '.ow-music{pointer-events:none}.ow-mu-btn,.ow-music.show .ow-mu-pop,.ow-music:focus-within .ow-mu-pop{pointer-events:auto}@media (hover:hover){.ow-music:hover .ow-mu-pop{pointer-events:auto}}' +
    /* the chat bubble is 58px at 20px from the corner: sit 14px above it, centred on it */
    '.ow-music.has-chat{right:calc(27px + env(safe-area-inset-right));bottom:calc(92px + env(safe-area-inset-bottom))}' +
    '.ow-mu-btn{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;padding:0;cursor:pointer;color:#241E19;' +
    'background:rgba(255,255,255,.62);border:1px solid rgba(255,255,255,.9);box-shadow:0 10px 26px -12px rgba(71,48,94,.55),inset 0 1px 0 rgba(255,255,255,.9),0 0 0 1px rgba(36,30,25,.10);' +
    '-webkit-backdrop-filter:blur(16px) saturate(140%);backdrop-filter:blur(16px) saturate(140%);transition:transform .15s ease}' +
    '.ow-mu-btn:hover{transform:scale(1.06)}.ow-mu-btn:focus-visible{outline:3px solid #14B8A6;outline-offset:3px}' +
    '.ow-mu-btn svg{width:20px;height:20px}' +
    '.ow-mu-pop{height:44px;display:flex;align-items:center;padding:0 14px;border-radius:22px;background:rgba(255,255,255,.62);border:1px solid rgba(255,255,255,.9);' +
    'box-shadow:0 10px 26px -12px rgba(71,48,94,.55),0 0 0 1px rgba(36,30,25,.10);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);' +
    'opacity:0;visibility:hidden;transform:translateX(8px);transition:opacity .18s ease,transform .18s ease,visibility 0s .18s}' +
    '.ow-music.show .ow-mu-pop,.ow-music:focus-within .ow-mu-pop{opacity:1;visibility:visible;transform:none;transition:opacity .18s ease,transform .18s ease}' +
    '@media (hover:hover){.ow-music:hover .ow-mu-pop{opacity:1;visibility:visible;transform:none;transition:opacity .18s ease,transform .18s ease}}' +
    '.ow-mu-pop input{width:112px;accent-color:#0D9488;margin:0;cursor:pointer}' +
    'html[data-theme="dark"] .ow-mu-btn,html.dark .ow-mu-btn,html[data-theme="dark"] .ow-mu-pop,html.dark .ow-mu-pop{background:rgba(21,27,37,.72);border-color:rgba(255,255,255,.18);color:#F8F8F5;box-shadow:0 10px 26px -12px rgba(0,0,0,.8),inset 0 1px 0 rgba(255,255,255,.08)}' +
    '@media print{.ow-music{display:none}}';
  var ICON_ON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>';
  var ICON_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="m16 9 5 6M21 9l-5 6"/></svg>';
  var wrap, btn, slider, hideT;

  function render() {
    if (!btn) return;
    var on = playing && !muted;
    btn.innerHTML = on ? ICON_ON : ICON_OFF;
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.setAttribute('aria-label', on ? T.off : T.on);
    btn.title = on ? T.off : T.on;
  }
  function peek() {
    wrap.classList.add('show');
    clearTimeout(hideT);
    hideT = setTimeout(function () { wrap.classList.remove('show'); }, 3500);
  }
  function placeAboveChat() {
    var chat = document.querySelector('script[src*="leadconnectorhq.com/loader.js"],chat-widget,#lc_text-widget,.lc_text-widget');
    wrap.classList.toggle('has-chat', !!chat);
  }

  function build() {
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    wrap = document.createElement('div'); wrap.className = 'ow-music';
    btn = document.createElement('button'); btn.type = 'button'; btn.className = 'ow-mu-btn';
    var pop = document.createElement('div'); pop.className = 'ow-mu-pop';
    slider = document.createElement('input'); slider.type = 'range'; slider.min = '0'; slider.max = '100'; slider.step = '1';
    slider.value = String(Math.round(vol * 100)); slider.setAttribute('aria-label', T.vol);
    pop.appendChild(slider); wrap.appendChild(btn); wrap.appendChild(pop);
    document.body.appendChild(wrap);
    placeAboveChat();
    setTimeout(placeAboveChat, 2500);
    /* the open chat panel covers this corner: step aside while it is open */
    setInterval(function () { wrap.style.display = document.querySelector('chat-widget[data-active="true"]') ? 'none' : ''; }, 400);
    btn.addEventListener('click', function () {
      if (playing && !muted) { muted = true; lsSet(KEY, 'off'); stop(); }
      else { muted = false; lsSet(KEY, 'on'); play(); peek(); }
      render();
    });
    slider.addEventListener('input', function () {
      setVol(slider.value / 100);
      if (slider.value > 0 && (muted || !playing)) { muted = false; lsSet(KEY, 'on'); play(); }
      peek();
    });
    render();
  }

  /* First interaction starts the music (unless the visitor turned it off). */
  var EVENTS = ['pointerdown', 'keydown', 'touchend', 'click', 'scroll'];
  function first(e) {
    if (e && e.target && wrap && wrap.contains(e.target)) return;   /* the control handles itself */
    if (muted) return;
    play();
    if (playing || (ctx && ctx.state === 'running')) EVENTS.forEach(function (n) { window.removeEventListener(n, first, true); });
  }
  EVENTS.forEach(function (n) { window.addEventListener(n, first, { capture: true, passive: true }); });

  document.addEventListener('visibilitychange', function () {
    if (!ctx || el) return;
    if (document.hidden) { if (ctx.state === 'running') ctx.suspend(); }
    else if (playing) ctx.resume();
  });
  window.addEventListener('pagehide', savePos);

  if (document.body) build(); else document.addEventListener('DOMContentLoaded', build);
})();
