/* Public marketing launch policy. This is a doorway rule, not an entitlement or route guard:
   authorized internal users can still visit the app origin directly. Keep the OAuth catcher
   above this script on every page; it must run before any marketing behavior. */
(function () {
  "use strict";

  var PUBLIC_APP_OPEN = Object.freeze({
    onehome: true, onejob: true, oneevent: true,
    onescore: true, onesocial: false, oneagent: true,
    onepay: true, onebusiness: true,
  });
  var APP_PATH = Object.freeze({
    home: "onehome", jobs: "onejob", events: "oneevent",
    onescore: "onescore", social: "onesocial", agent: "oneagent",
    pay: "onepay", business: "onebusiness",
  });
  var MARKETING_DOORWAY = Object.freeze({
    "onescore.oneworldlabs.ai": "onescore",
    "onesocial.oneworldlabs.ai": "onesocial",
    "oneagent.oneworldlabs.ai": "oneagent",
    "onepay.oneworldlabs.ai": "onepay",
  });
  var NAME = Object.freeze({
    onehome: "OneHome", onejob: "OneJob", oneevent: "OneEvent",
    onescore: "OneScore", onesocial: "OneSocial", oneagent: "OneAgent",
    onepay: "OnePay", onebusiness: "OneBusiness",
  });
  var COPY = {
    en: { soon: "Coming soon", title: "Coming soon: {name}", body: "{name} is not open to the public yet. You can still explore what it will offer.", details: "View details", close: "Close", apps: "One app, one login. OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore and OneAgent are open now.", platform: "Eight apps for small businesses and freelancers, all under one login.", business: "Open now · One login across One World", businessFaq: "OneBusiness is open now. Sign in with your One ID." },
    co: { soon: "Próximamente", title: "Próximamente: {name}", body: "{name} todavía no está abierta al público. Puede conocer lo que ofrecerá.", details: "Ver detalles", close: "Cerrar", apps: "Una app, un solo inicio de sesión. OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore y OneAgent ya están abiertas.", platform: "Ocho apps para pequeños negocios e independientes, con un solo inicio de sesión.", business: "Abierta ahora · Un solo inicio de sesión en One World", businessFaq: "OneBusiness ya está abierta. Inicie sesión con su One ID." },
    es: { soon: "Próximamente", title: "Próximamente: {name}", body: "{name} aún no está abierta al público. Puedes conocer lo que ofrecerá.", details: "Ver detalles", close: "Cerrar", apps: "Una app, un solo inicio de sesión. OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore y OneAgent ya están abiertas.", platform: "Ocho apps para pequeñas empresas y autónomos, con un solo inicio de sesión.", business: "Abierta ahora · Un solo inicio de sesión en One World", businessFaq: "OneBusiness ya está abierta. Inicia sesión con tu One ID." },
    de: { soon: "Demnächst", title: "Demnächst: {name}", body: "{name} ist noch nicht öffentlich verfügbar. Sie können sich bereits über die geplanten Funktionen informieren.", details: "Details ansehen", close: "Schließen", apps: "Eine App, ein Login. OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore und OneAgent sind jetzt verfügbar.", platform: "Acht Apps für kleine Unternehmen und Selbstständige, mit einem Login.", business: "Jetzt verfügbar · Ein Login für One World", businessFaq: "OneBusiness ist jetzt verfügbar. Melden Sie sich mit Ihrer One ID an." },
    ru: { soon: "Скоро", title: "Скоро: {name}", body: "{name} пока не доступно всем пользователям. Вы можете узнать о планируемых возможностях.", details: "Подробнее", close: "Закрыть", apps: "Одно приложение, один вход. OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore и OneAgent уже доступны.", platform: "Восемь приложений для малого бизнеса и фрилансеров. Один вход для всех.", business: "Уже доступно · Один вход в One World", businessFaq: "OneBusiness уже доступно. Войдите с One ID." },
    zh: { soon: "即将推出", title: "即将推出：{name}", body: "{name} 尚未向公众开放。你仍可了解它将提供的功能。", details: "查看详情", close: "关闭", apps: "一个应用，一次登录。OneBusiness、OneEvent、OneRide、OneHome、OnePay、OneJob、OneScore 和 OneAgent 现已开放。", platform: "面向小企业和自由职业者的八款应用，共用一次登录。", business: "现已开放 · One World 共用一次登录", businessFaq: "OneBusiness 现已开放。使用你的 One ID 登录。" },
    pt: { soon: "Em breve", title: "Em breve: {name}", body: "{name} ainda não está aberto ao público. Você já pode conhecer o que ele vai oferecer.", details: "Ver detalhes", close: "Fechar", apps: "Um app, um login. OneBusiness, OneEvent, OneRide, OneHome, OnePay, OneJob, OneScore e OneAgent já estão disponíveis.", platform: "Oito apps para pequenos negócios e autônomos, com um único login.", business: "Disponível agora · Um único login no One World", businessFaq: "OneBusiness já está disponível. Entre com seu One ID." },
  };
  var dialog, title, body, details, closeButton, activeKey, returnFocus;

  function locale() {
    var selected = window.OWL_LANG || document.documentElement.lang || "en";
    if (selected.toLowerCase().indexOf("es-co") === 0) selected = "co";
    else selected = selected.toLowerCase().split("-")[0];
    return COPY[selected] ? selected : "en";
  }
  function words() { return COPY[locale()]; }
  function detailsPath(key) { return "/apps/" + key + "/"; }
  function appFromUrl(href) {
    try {
      var url = new URL(href, location.href);
      if (url.hostname !== "app.oneworldlabs.ai") return null;
      return APP_PATH[url.pathname.split("/")[1]] || null;
    } catch (_) { return null; }
  }
  function appFromCard(card) {
    var learn = card.querySelector('a.app-learn[href^="/apps/"]');
    var match = learn && learn.getAttribute("href").match(/^\/apps\/(onehome|onejob|oneevent|onescore|onesocial|oneagent|onepay|onebusiness)\//);
    return match ? match[1] : null;
  }
  function makeButton(old, key, className) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = className || old.className || "";
    button.style.minHeight = "44px";
    button.dataset.publicApp = key;
    button.addEventListener("click", function () { show(key, button); });
    old.replaceWith(button);
    updateButton(button);
    return button;
  }
  function updateButton(button) {
    var key = button.dataset.publicApp;
    button.textContent = words().soon;
    button.setAttribute("aria-label", words().soon + ": " + NAME[key]);
    button.setAttribute("title", words().soon + ": " + NAME[key]);
  }
  function ensureDialog() {
    if (dialog) return;
    var style = document.createElement("style");
    style.textContent = ".owl-launch-dialog{width:min(420px,calc(100vw - 32px));max-height:calc(100vh - 32px);margin:auto;padding:28px;border:1px solid rgba(47,43,39,.14);border-radius:22px;background:#FAFAF8;color:#241E19;box-shadow:0 24px 70px rgba(11,15,26,.26);font:inherit}.owl-launch-dialog::backdrop{background:rgba(11,15,26,.56)}.dark .owl-launch-dialog{background:#151b25;color:#f8f8f5;border-color:rgba(255,255,255,.16)}.owl-launch-dialog h2{margin:0 0 10px;font-size:1.4rem;font-weight:800;line-height:1.2}.owl-launch-dialog p{margin:0 0 22px;line-height:1.55}.owl-launch-actions{display:flex;flex-wrap:wrap;gap:10px}.owl-launch-actions a,.owl-launch-actions button{display:inline-flex;min-height:44px;align-items:center;justify-content:center;padding:0 16px;border-radius:12px;font:inherit;font-weight:700;text-decoration:none}.owl-launch-actions a{background:#4A4038;color:white}.owl-launch-actions button{border:1px solid currentColor;background:transparent;color:inherit}.owl-launch-actions a:focus-visible,.owl-launch-actions button:focus-visible{outline:3px solid #14B8A6;outline-offset:3px}";
    document.head.appendChild(style);
    dialog = document.createElement("dialog");
    dialog.className = "owl-launch-dialog";
    dialog.setAttribute("aria-labelledby", "owl-launch-title");
    dialog.setAttribute("aria-describedby", "owl-launch-body");
    title = document.createElement("h2"); title.id = "owl-launch-title";
    body = document.createElement("p"); body.id = "owl-launch-body";
    var actions = document.createElement("div"); actions.className = "owl-launch-actions";
    details = document.createElement("a");
    closeButton = document.createElement("button"); closeButton.type = "button";
    closeButton.addEventListener("click", function () { dialog.close(); });
    actions.append(details, closeButton);
    dialog.append(title, body, actions);
    dialog.addEventListener("close", function () { if (returnFocus && returnFocus.isConnected) returnFocus.focus(); });
    dialog.addEventListener("click", function (event) { if (event.target === dialog) dialog.close(); });
    document.body.appendChild(dialog);
  }
  function updateDialog() {
    if (!dialog || !activeKey) return;
    var copy = words(), name = NAME[activeKey];
    title.textContent = copy.title.replace("{name}", name);
    body.textContent = copy.body.replace("{name}", name);
    details.textContent = copy.details;
    details.href = detailsPath(activeKey);
    closeButton.textContent = copy.close;
  }
  function show(key, trigger) {
    ensureDialog();
    activeKey = key;
    returnFocus = trigger;
    updateDialog();
    dialog.showModal();
    closeButton.focus();
  }
  function syncCopy() {
    document.querySelectorAll("[data-public-app]").forEach(updateButton);
    var copy = words();
    document.querySelectorAll('[data-i18n="apps_sub"]').forEach(function (el) { el.textContent = copy.apps; });
    document.querySelectorAll('[data-i18n="div_pl_p"]').forEach(function (el) { el.textContent = copy.platform; });
    document.querySelectorAll('[data-i18n="ob_available"]').forEach(function (el) { el.textContent = copy.business; });
    document.querySelectorAll('[data-i18n="ob_faq_when_body"]').forEach(function (el) { el.textContent = copy.businessFaq; });
    updateDialog();
  }
  function init() {
    /* Card detail links are untouched. Their launch side becomes an honest button. */
    document.querySelectorAll("#apps .app-card").forEach(function (card) {
      var key = appFromCard(card);
      if (!key || PUBLIC_APP_OPEN[key]) return;
      var action = card.querySelector("a.app-open, a.app-open-strip, .coming-label");
      if (!action) action = card.querySelector(".app-foot > span");
      if (!action) return;
      makeButton(action, key, action.closest(".app-foot") ? "app-open-strip inline-flex items-center font-semibold hue-text" : "app-open");
    });
    /* Existing menu/footer links go to the marketing detail page. Any other public
       launch CTA opens the dialog, including CTAs on the marketing detail page itself. */
    document.querySelectorAll("a[href]").forEach(function (link) {
      try {
        var doorway = MARKETING_DOORWAY[new URL(link.href, location.href).hostname];
        if (doorway && !PUBLIC_APP_OPEN[doorway]) link.href = detailsPath(doorway);
      } catch (_) { /* malformed links are left alone */ }
      var key = appFromUrl(link.href);
      if (!key || PUBLIC_APP_OPEN[key]) return;
      if (link.classList.contains("menu-navitem") || link.closest("nav,footer")) {
        link.href = detailsPath(key);
      } else {
        makeButton(link, key);
      }
    });
    document.addEventListener("click", function (event) {
      var link = event.target.closest && event.target.closest("a[href]");
      var key = link && appFromUrl(link.href);
      if (!key || PUBLIC_APP_OPEN[key]) return;
      event.preventDefault();
      show(key, link);
    }, true);
    new MutationObserver(syncCopy).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
    syncCopy();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
  window.OWL_PUBLIC_APP_OPEN = PUBLIC_APP_OPEN;
})();
