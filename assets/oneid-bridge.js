/* ============================================================================
   ONE WORLD — session bridge (localStorage  <->  parent-domain cookie)
   ----------------------------------------------------------------------------
   Lee: "If you sign in to one app, you sign in to all of the apps… you sign out
   of one app, you sign out of all the apps. Like Google."

   THE PROBLEM THIS CLOSES
   Every app used to live under www.oneworldlabs.ai/<app>/, so they all shared
   one ORIGIN and therefore one localStorage — cross-app sign-in worked by
   accident. Now each app answers on its own hostname, and a new hostname is a
   new, empty store. The accident is over.

   OneJob already writes the session to a cookie on the parent domain
   `.oneworldlabs.ai`, which every subdomain can read. But the session only
   STARTS somewhere, and for most people that somewhere is this page — they sign
   in with One ID on the homepage. Without this file, the session sits in this
   origin's localStorage, no cookie is ever written, and every subdomain still
   asks for a fresh sign-in. The plumbing exists; this is what puts water in it.

   WHAT IT DOES
   Keeps localStorage and the shared cookie in step, in both directions:

     · session here, no cookie      → write the cookie   (this is the bootstrap)
     · cookie, nothing here         → adopt it           (arriving already signed in)
     · session gone from here       → clear the cookie   (sign out means everywhere)

   It is a SYNC, not an auth system. It never mints, refreshes or validates a
   token — it only moves one the SDK already produced. If it fails, the app is
   exactly as signed-in as it was before.

   WHY A COOKIE
   Cookies are scoped to a DOMAIN; localStorage is scoped to an ORIGIN. Only the
   cookie can span onejob./onescore./oneevent./onesocial./oneagent. Same model
   as Google: authenticate once, and mail./drive./docs. all see it.

   CARE TAKEN
   · CHUNKED. A cookie caps near 4KB and a Supabase session can exceed it. A
     silently truncated session parses as garbage, which a user experiences as
     "it logged me out at random" — the worst possible failure here.
   · SameSite=Lax, not None. Every app is same-site to every other, so Lax is
     enough, and it keeps these tokens off genuinely cross-site requests.
   · Secure everywhere except localhost, where there is no HTTPS to be secure over.
   · Not HttpOnly — it cannot be. The browser SDK has to read the token to attach
     it to requests. That is the exposure localStorage already had, not a new one.
   · Off-domain hosts (localhost, previews, onesocial.ai) are left alone. A cookie
     cannot cross a registrable-domain boundary and pretending otherwise would
     fail silently.

   Delete this file for an app once that app ships the real storage adapter
   (OneJob's src/lib/sessionStorage.ts). Until then it is what makes One ID one.
   ========================================================================== */
(function () {
  "use strict";

  var KEY = "sb-wseblryyqxawvbjmylbo-auth-token";
  var DOMAIN = "oneworldlabs.ai";
  var CHUNK = 3200;
  var MAX_CHUNKS = 24;

  function onDomain() {
    var h = location.hostname;
    return h === DOMAIN || h.slice(-(DOMAIN.length + 1)) === "." + DOMAIN;
  }
  if (!onDomain()) return;

  function attrs() {
    var secure = location.protocol === "https:" ? "; Secure" : "";
    return "; Domain=." + DOMAIN + "; Path=/; Max-Age=34560000; SameSite=Lax" + secure;
  }
  function readRaw(name) {
    var target = encodeURIComponent(name) + "=";
    var parts = document.cookie.split("; ");
    for (var i = 0; i < parts.length; i++) {
      if (parts[i].indexOf(target) === 0) return decodeURIComponent(parts[i].slice(target.length));
    }
    return null;
  }
  function writeRaw(name, value) {
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + attrs();
  }
  function deleteRaw(name) {
    document.cookie = encodeURIComponent(name) + "=; Domain=." + DOMAIN + "; Path=/; Max-Age=0; SameSite=Lax";
  }

  function readCookie() {
    var single = readRaw(KEY);
    if (single !== null) return single;
    /* Stop at the first gap. A missing middle chunk means the value is
       incomplete, and half a session is worse than none. */
    var out = "";
    for (var i = 0; i < MAX_CHUNKS; i++) {
      var part = readRaw(KEY + "." + i);
      if (part === null) break;
      out += part;
    }
    return out || null;
  }

  function clearCookie() {
    deleteRaw(KEY);
    for (var i = 0; i < MAX_CHUNKS; i++) deleteRaw(KEY + "." + i);
  }

  function writeCookie(value) {
    clearCookie();                       /* never let an old chunk tail onto a new value */
    if (value.length <= CHUNK) { writeRaw(KEY, value); return; }
    for (var i = 0, o = 0; o < value.length; i++, o += CHUNK) {
      writeRaw(KEY + "." + i, value.slice(o, o + CHUNK));
    }
  }

  function local() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function valid(raw) {
    if (!raw) return false;
    try {
      var s = JSON.parse(raw);
      return !!(s && s.access_token && s.refresh_token);
    } catch (e) { return false; }
  }

  /* Remember what we last saw locally, so a session DISAPPEARING from
     localStorage can be told apart from one that was never there. Only the
     former is a sign-out, and only a sign-out should clear the cookie. */
  var SEEN = "ow_bridge_had_session";

  function sync() {
    try {
      var here = local();
      var there = readCookie();
      var hadBefore = false;
      try { hadBefore = sessionStorage.getItem(SEEN) === "1"; } catch (e) {}

      if (valid(here)) {
        try { sessionStorage.setItem(SEEN, "1"); } catch (e) {}
        if (here !== there) writeCookie(here);      /* bootstrap / refresh */
        return;
      }

      if (valid(there)) {
        if (hadBefore) {
          /* We watched a session vanish from this origin. That is a sign-out,
             and Lee's rule is that signing out of one app signs you out of all
             of them — so the cookie goes too. */
          clearCookie();
          try { sessionStorage.removeItem(SEEN); } catch (e) {}
        } else {
          /* Arrived already signed in elsewhere. Adopt it so this origin's app
             sees a session without a second login. */
          try { localStorage.setItem(KEY, there); } catch (e) {}
          try { sessionStorage.setItem(SEEN, "1"); } catch (e) {}
        }
      }
    } catch (e) {
      /* Never let a sync problem break the page it is riding on. */
      try { console.warn("[oneworld-bridge]", e); } catch (_) {}
    }
  }

  sync();
  /* The SDK writes the token asynchronously after an OAuth redirect, and other
     tabs can sign in or out while this one is open. */
  window.addEventListener("storage", function (e) { if (!e.key || e.key === KEY) sync(); });
  window.addEventListener("focus", sync);
  var ticks = 0;
  var t = setInterval(function () { sync(); if (++ticks > 20) clearInterval(t); }, 1500);
})();
