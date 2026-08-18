/** ============================================================================================
 *  The Tailwind configuration for www.oneworldlabs.ai.
 *
 *  This is a VERBATIM port of the `tailwind.config = {…}` object that used to sit inline in all
 *  17 pages and was fed to the Play CDN at runtime. Byte-identical in every page, verified before
 *  the port. Nothing was redesigned; the only change is WHERE it runs — here, at build time,
 *  instead of in each visitor's browser.
 *
 *  Every colour resolves to a CSS custom property that the pages already declare in their own
 *  <style> blocks, so light and dark theming keeps working exactly as it did.
 * ==========================================================================================*/
module.exports = {
  darkMode: 'class',
  /* Every page that carries Tailwind classes. Add new pages here or their utilities will not be
     generated — that is the one real cost of leaving the CDN behind, and it is why the CI check
     in .github/workflows/css.yml exists. */
  content: ['./**/*.html', '!./node_modules/**'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: { DEFAULT: 'var(--ow-primary)', foreground: 'var(--ow-primary-fg)' },
        secondary: 'var(--color-secondary)',
        background: 'var(--color-bg)',
        foreground: 'var(--color-fg)',
        border: 'var(--color-border)',
        card: 'var(--color-card)',
        muted: { DEFAULT: 'var(--color-secondary)', foreground: 'var(--color-muted)' },
      },
    },
  },
  plugins: [],
}
