/* Website light/dark theme (UI "full-page theme framing", approved 17 Oct; integrated by PUB30 18 Oct).
   Independent of One ID and app preferences. The early head script sets data-theme before first paint;
   this file adds the footer switch, keeps following the system setting until the visitor chooses, and
   labels the switch in all seven site languages. Loaded once per page. */
(function () {
  var root = document.documentElement, system = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  var L = {
    en: ['Use light mode', 'Use dark mode'], co: ['Usar modo claro', 'Usar modo oscuro'], es: ['Usar modo claro', 'Usar modo oscuro'],
    de: ['Hellen Modus verwenden', 'Dunklen Modus verwenden'], ru: ['Светлая тема', 'Тёмная тема'],
    zh: ['使用浅色模式', '使用深色模式'], pt: ['Usar modo claro', 'Usar modo escuro']
  };
  var choice = null;
  try { choice = localStorage.getItem('owl_site_theme'); } catch (e) {}
  if (choice !== 'light' && choice !== 'dark') choice = null;
  var button = document.createElement('button');
  button.type = 'button'; button.className = 'site-theme-toggle';
  function render() {
    var dark = (choice || (system && system.matches ? 'dark' : 'light')) === 'dark';
    root.setAttribute('data-theme', dark ? 'dark' : 'light');
    var t = L[window.OWL_LANG] || L.en;
    button.textContent = dark ? t[0] : t[1];
    button.setAttribute('aria-pressed', dark ? 'true' : 'false');
  }
  button.addEventListener('click', function () {
    choice = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('owl_site_theme', choice); } catch (e) {}
    render();
  });
  if (system) { try { system.addEventListener('change', render); } catch (e) { system.addListener && system.addListener(render); } }
  document.addEventListener('ow:lang', render);
  var footer = document.querySelector('footer');
  if (footer && !footer.querySelector('.site-theme-toggle')) footer.appendChild(button);
  render();
})();
