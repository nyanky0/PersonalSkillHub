# Dark mode + expandable rows — proven recipe (Carbon IBM landing page)

Session-proven on the Maul landing page (Laravel 12 + Tailwind 4 + Vite, IBM Carbon
design tokens). Carbon dark palette: page #161616, layer #262626, layer-2 #1c1c1c,
border #393939, text #f4f4f4, muted #c6c6c6, muted-2 #a8a8a8, accent text #78a9ff.

## Token map (light → dark)

| Semantic token | Light | Dark | Replaces |
|---|---|---|---|
| `ink` | #161616 | #f4f4f4 | text-carbon-100 |
| `muted` | #525252 | #c6c6c6 | text-carbon-70 |
| `muted-2` | #6f6f6f | #a8a8a8 | text-carbon-60 |
| `surface` | #ffffff | #262626 | bg-white |
| `surface-2` | #f4f4f4 | #1c1c1c | bg-carbon-10 |
| `line` | #e0e0e0 | #393939 | border-carbon-20, bg-carbon-20 (gap grids), divide-carbon-20 |
| `accent-soft` | #edf5ff | rgba(15,98,254,0.15) | bg-blue-10 |
| `accent-strong` | #0043ce | #78a9ff | text-blue-70 |
| `section-dark` | #161616 | #262626 | bg-carbon-100 on ALWAYS-dark sections |

Keep FIXED (never flip): `carbon-30/10` + `white` text on always-dark sections,
`carbon-80` borders/divides there, `blue-60` interactive accents, `blue-10` text on dark.

## @theme + .dark wiring

```css
@theme { --color-ink: #161616; /* ...all semantic tokens, light values... */ }

/* explicit dark choice (JS adds class) */
.dark { --color-ink: #f4f4f4; /* ...dark values... */ color-scheme: dark; }

/* system preference, only when no explicit choice */
@media (prefers-color-scheme: dark) {
  :root:not(.light) { /* same dark values */ }
}
```

Cascade order that makes it work: unlayered `.dark` and `:root:not(.light)` both beat
Tailwind's `@layer theme :root`. `.light` class (added by JS) defeats the media block.
FOUC script (head, before vite css):

```html
<script>
(function(){try{var s=localStorage.getItem('maul-theme');
var d=s?s==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.classList.toggle('dark',d);}catch(e){}})();
</script>
```

Toggle JS (app.js):

```js
const toggles = document.querySelectorAll('.theme-toggle');
const rootEl = document.documentElement;
const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
const applyTheme = (dark, persist=false) => {
  rootEl.classList.toggle('dark', dark);
  toggles.forEach(btn => {
    btn.setAttribute('aria-pressed', String(dark));
    btn.querySelector('.icon-sun')?.classList.toggle('hidden', !dark); // dark → show sun
    btn.querySelector('.icon-moon')?.classList.toggle('hidden', dark);
  });
  if (persist) { try { localStorage.setItem('maul-theme', dark?'dark':'light'); } catch(e){} }
};
if (toggles.length) {
  applyTheme(rootEl.classList.contains('dark'));
  toggles.forEach(btn => btn.addEventListener('click', () =>
    applyTheme(!rootEl.classList.contains('dark'), true)));
  darkQuery.addEventListener('change', e => { if (!localStorage.getItem('maul-theme')) applyTheme(e.matches); });
}
```

Themeable one-offs: hero dot grid `background-image: radial-gradient(circle, var(--grid-dot) 1px, transparent 1px)` with `:root { --grid-dot: rgba(22,22,22,.12) }` and `.dark { --grid-dot: rgba(244,244,244,.09) }`. Gradient section dividers use `var(--color-line)`.

## Expandable project rows

Grid-rows disclosure, no height math:

```css
.project-detail { display:grid; grid-template-rows:0fr; visibility:hidden;
  transition: grid-template-rows .35s ease, visibility .35s; }
.project-detail > div { overflow:hidden; }
.project-detail.open { grid-template-rows:1fr; visibility:visible; }
.project-toggle-icon { transition: transform .2s ease; }
.project-toggle-icon.rotated { transform: rotate(45deg); } /* plus → × */
```

```js
document.querySelectorAll('.project-toggle').forEach(btn => {
  const panel = document.getElementById(btn.getAttribute('aria-controls'));
  if (!panel) return;
  btn.addEventListener('click', () => {
    const open = !panel.classList.contains('open');
    panel.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.querySelector('.project-toggle-icon')?.classList.toggle('rotated', open);
  });
});
```

Markup: row `<div class="relative ...">`, inner grid `pr-8 lg:pr-0` so text clears the
absolute button (`right-0 lg:-right-6 top-1/2 -translate-y-1/2`); panel after the grid
with `role="region"` + `aria-label`. Add all transitions to the reduced-motion block.

## Verification (no vision provider)

Check computed styles per theme via browser_console:

```js
// dark assertions
document.documentElement.classList.contains('dark') === true
getComputedStyle(document.body).backgroundColor === 'rgb(22, 22, 22)'
getComputedStyle(document.body).color === 'rgb(244, 244, 244)'
getComputedStyle(document.querySelector('article')).backgroundColor === 'rgb(38, 38, 38)'
// always-dark sections: bg-section-dark === 'rgb(38, 38, 38)' in dark, 'rgb(22, 22, 22)' in light
```

Toggle twice (dark→light→dark) and assert localStorage round-trip + icon visibility swap.
Expand: assert `aria-expanded`, `.open`, `.rotated` after click; panel height > 0 after
transition (~350ms). CAUTION: `getBoundingClientRect().height` is 0 DURING the 0.35s
grid-rows transition — check after the transition or programmatically click twice.

## Bulk-rename substring pitfall (real bug)

`replace_all 'bg-carbon-10' → 'bg-surface-2'` BEFORE `'bg-carbon-100' → 'bg-section-dark'`
turned every `bg-carbon-100` into `bg-surface-20` (nonexistent class → transparent bg,
header/stats/contact sections vanished). sed/python str.replace are naive substring ops.
Rule: longest-first ordering, then audit:
`grep -oE 'bg-[a-z-]*[0-9]+' resources/views/*.blade.php | sort | uniq -c`
Any remaining numbered light-section tokens = missed swaps. After blade changes,
re-render dist/index.html (`artisan serve` + curl + sed strip host — see
vercel-static-deploy references/laravel-static-export.md) — sed-ing only the asset hash
into a stale HTML keeps old class names.
