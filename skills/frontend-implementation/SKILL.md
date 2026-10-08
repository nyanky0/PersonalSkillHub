---
name: frontend-implementation
description: "Build and verify production web UI pages, components, and layout responsiveness."
version: 1.0.0
tags: [frontend, css, tailwind, vite, laravel, animation, verification, wsl]
platforms: [linux, macos, windows]
triggers:
  - build a landing page
  - make a portfolio page
  - tailwind classes not applying
  - add animations to a page
  - verify UI in browser
  - scroll reveal animation
  - serve laravel from wsl
---

# Frontend Implementation

Build-and-verify knowledge for static/SSR web UI work (landing pages, portfolios, marketing pages) on the Tailwind 4 + Vite + Laravel stack, including the WSL + Windows PHP (Laragon) environment. Pair with `frontend-design` (aesthetic direction) and `popular-web-designs` (design-system templates) — this skill covers the mechanical layer: build loop, animation pitfalls, verification.

## Build loop (Tailwind 4 + Vite + Laravel)

1. `resources/views/*.blade.php` = markup, `resources/css/app.css` = Tailwind source, `resources/js/app.js` = vanilla JS (no framework needed for landing pages).
2. After ANY edit that introduces a Tailwind class never used before, run `npm run build`. Tailwind scans source files at build time — a new class is NOT live in dev without a rebuild.
3. Blade edits render on the next request (no rebuild needed for pure HTML changes); CSS/JS changes need `npm run build`.
4. Custom design tokens go in `@theme { --color-<name>: ... }` in app.css; custom CSS classes in `@layer base` or plain rules; keyframe-driven one-offs as `@utility` so Tailwind variants (`motion-safe:`) apply.

## CSS animation pitfalls

- **`animation-fill-mode: both` holds the final keyframe forever and overrides hover transforms.** If the animation's `to` block has `transform: none`, a `:hover { transform: scale(...) }` on the same element silently never fires. Fix: `backwards` (applies `from` during delay, releases after finish) or animate `opacity` only.
- **Reveal hidden state must be JS-gated**: `document.documentElement.classList.add('js')` in JS, then `.js .reveal { opacity:0; ... }` / `.js .reveal.is-visible { opacity:1 }`. No-JS users see content; a missing-JS flash of invisible content never happens.
- **Reduced motion**: gate animations with `motion-safe:` variants (Tailwind) and add a `@media (prefers-reduced-motion: reduce)` block disabling transitions/animations on reveal, draw-line, cursor, and counters. Count-up/counters should set the final value instantly when reduced motion matches.
- **Stagger via CSS variable**: give each item `style="--d: Nms"` and use `transition-delay: var(--d)` — cleaner than per-item classes. Cap total stagger (~300ms) so the section doesn't feel slow.
- **`scroll-behavior: smooth`** on `html` + `scroll-mt-*` on anchored sections (offset for sticky headers). Disable smooth under reduced motion.
- **Custom lerp smooth-scroll conflicts with IntersectionObserver reveals.** A rAF loop calling `window.scrollTo(0, cur)` every frame fires scroll events so fast the IO threshold never settles — reveal classes never trigger (stuck at 3/11). Native `scroll-behavior: smooth` or Lenis (drives a transform, not scrollTo) both keep IO working. Never hand-roll scrollTo lerp over an IO reveal page.
- **`HTMLCollection` has no `.forEach`** — `dotsWrap.children.forEach(...)` throws mid-handler, so state set AFTER the call (counter, active dot) silently never runs while the animation BEFORE it already executed: slides move but indicators stay frozen, console shows a burst of empty-message exceptions. `querySelectorAll` returns NodeList (has forEach); `.children` returns HTMLCollection (doesn't). Fix: `Array.from(x.children).forEach(...)`.
- **Premium animation recipe (Pier88-style)**: Lenis smooth scroll init + required CSS, blur-reveal system, split-line heading reveal, GSAP carousel with `power3.out` + 0.04 stagger — full copy-paste code in `references/premium-animation-recipe.md`.
- **Parallax without a library = scroll → CSS var**: rAF loop with `ticking` guard; compute progress from `getBoundingClientRect`, write `--x` custom prop per frame, element does `transform: translateY(var(--x))`. Element and background move OPPOSITE directions for depth. Full Pier88-deconstructed code (hero plate exit + bg drift) in `references/premium-animation-recipe.md` §5.
- **Sticky-pin scroll section**: container `position:relative` + tall height (~5000px), inner `.pin { position:sticky }` — scroll progress over the tall container drives element transforms. The premium "plate journey" scroll feel.
- **Carousel init bug**: `gsap.set(slides.slice(1), {xPercent:100, autoAlpha:0})` at init — without it all slides stack visible until first auto-advance fires.
- **Vanilla slider (no GSAP): slides MUST be `position:absolute; inset:0` inside a `position:relative` slider (`min-height` set, or absolute collapses it).** `display:flex` + `translateX((i-current)*100%)` is the classic trap: in a flex row, translateX is relative to each slide's flex slot, so the "active" slide sits at `left: sliderLeft + width` — offscreen, reads as blank. With absolute anchoring, `translateX` is relative to the slider box and the active slide always lands centered. Also: slider imgs need `loading="eager"` (lazy + translated offscreen = never loaded = blank slide); `el.children.forEach` (HTMLCollection) throws — `Array.from(el.children)`.
- **Ken Burns + parallax transform conflict**: CSS keyframe animation and JS-driven transform both write `transform` on one element — keyframe wins/glitches. Split: animation on inner `img`, parallax `translateY` on wrapper div (`inset:-6%` so translate doesn't expose edges).
- Keep animation to `transform`/`opacity` only (compositor-friendly); `transition: all` and blurred reveal animations read as AI-slop.
- **Expand/collapse rows (disclosure)**: animate `grid-template-rows: 0fr → 1fr` on a wrapper + `overflow: hidden` on its child — no JS height math, smooth in both directions. Add `visibility: hidden → visible` so collapsed content leaves the a11y tree. Button: `aria-expanded` + `aria-controls`, rotate a plus icon 45° (`.rotated`) for the open state.
- **Dead-script symptoms (module JS)**: a duplicate `const X` declaration anywhere in the module = SyntaxError → ENTIRE script dies, page stays blank, loading overlay never hides. `node --check` on the extracted `<script>` catches it (extract via `python3 -c "import re;open('/tmp/x.js','w').write(re.search(r'<script[^>]*>(.*?)</script>', open('f.html').read(), re.S).group(1))"`). A **called-but-undefined function** (e.g. `drawParticles()` referenced, never defined) survives `node --check` but throws ReferenceError every frame — grep call sites vs `function X` definitions and diff.
- **Don't trust terminal `��` in tool-written HTML**: emoji written via `write_file`/`patch` can DISPLAY as `��` in terminal but the FILE is valid UTF-8. Verify with `python3 -c "print(open('f',encoding='utf-8').read().count('\ufffd'))"` + `repr()` the region before "fixing" — only `\ufffd` in the file is real corruption.

## Dark mode via CSS-variable semantic tokens (Tailwind 4)

No `dark:` variants, no per-element class swapping. Define SEMANTIC tokens in `@theme` (light values), flip the same var names under a `.dark` class on `<html>` — every utility using them (`text-ink`, `bg-surface`, `border-line`) re-resolves automatically:

```css
@theme {
  --color-ink: #161616;          /* primary text */
  --color-muted: #525252;        /* body text */
  --color-muted-2: #6f6f6f;      /* labels/dates */
  --color-surface: #ffffff;      /* cards */
  --color-surface-2: #f4f4f4;    /* alt section bg */
  --color-line: #e0e0e0;         /* borders/dividers */
  --color-accent-soft: #edf5ff;  /* tint bg (was blue-10) */
  --color-accent-strong: #0043ce; /* text on tint (was blue-70) */
  --color-section-dark: #161616; /* always-dark sections, flips LIGHTER */
}
.dark {
  --color-ink: #f4f4f4; --color-muted: #c6c6c6; --color-muted-2: #a8a8a8;
  --color-surface: #262626; --color-surface-2: #1c1c1c; --color-line: #393939;
  --color-accent-soft: rgba(15, 98, 254, 0.15); --color-accent-strong: #78a9ff;
  --color-section-dark: #262626;
  color-scheme: dark;
}
```

Key mechanics:
- Unlayered `.dark {}` beats Tailwind's `@layer theme :root` regardless of specificity. If also honoring `prefers-color-scheme`, wrap the media block as `:root:not(.light)` so an explicit `.light` class can override the OS setting.
- **Always-dark sections** (header, stats band, footer) must NOT reuse a flipping token — give them `--color-section-dark` which flips to a LIGHTER dark (#262626) so they stay distinct from the #161616 page bg.
- **FOUC script**: inline in `<head>` BEFORE the vite CSS link — read `localStorage.getItem('maul-theme')`, else `matchMedia('(prefers-color-scheme: dark)')`, then `document.documentElement.classList.add('dark')`.
- **Toggle buttons**: shared `.theme-toggle` class, `aria-pressed`, persist choice to localStorage; `matchMedia` `change` listener follows OS only when no stored choice. Icon semantics: show the ACTION's icon — dark mode shows SUN, light shows MOON (easy to invert by mistake).
- Themeable one-offs (dot-grid textures, gradient dividers) must use `var(--grid-dot)` / `var(--color-line)` so they flip too.
- Swap hardcoded classes to semantic ones (`text-carbon-100`→`text-ink`, `bg-white`→`bg-surface`, `border-carbon-20`→`border-line`, `bg-blue-10`→`bg-accent-soft`); keep raw `carbon-*`/`text-white` only on always-dark sections.

Full token table, toggle JS, and verification: `references/dark-mode-and-expand.md`.

## Bulk class renames — substring collision pitfall

Doing a token rename sweep with `replace_all`/sed across a blade file: **longer tokens must be replaced BEFORE their prefixes**, or they get clobbered. Real case: replacing `bg-carbon-10` → `bg-surface-2` ran first and silently rewrote `bg-carbon-100` → `bg-surface-20` (a class that doesn't exist → transparent background, section visually vanishes). Order longest-first (`bg-carbon-100` before `bg-carbon-10`), and ALWAYS verify after the sweep: `grep -oE 'bg-[a-z-]+[0-9]{2,}' file | sort -u` should show no leftover numbered tokens on light sections.

## Verification without a vision provider

When vision analysis is unavailable, verify with a computed-style/DOM audit via `browser_console` — see `scripts/verify-ui.js` for a ready-to-paste expression. Check: font family/weight/size, colors, border-radius, rendered vs natural image size, horizontal overflow (`getBoundingClientRect().right > innerWidth`), `getAnimations()` fill-mode state, `document.fonts.check()`. Note: headless browsers block `window.resizeTo` — verify responsive behavior by CSS structure (breakpoint classes), not viewport resizing. Also: **async image loads** — right after navigation `img.complete && naturalWidth>0` can read 0/5 loaded; wait ~1s (`Promise`+`setTimeout`) before judging broken images. And **init success ≠ render OK**: check the loading overlay `classList.contains('hidden')` + status text not stuck on "initializing" + canvas painted (`getImageData` non-black) — those prove the render loop actually runs, which 0 console errors alone doesn't (a SyntaxError kills the script with NO console output). `getUserMedia` failing with "Requested device not found" in headless is the sandbox, not the code — only worry if the error is uncaught.

### Cloning a source site's data but NOT its design

When rebuilding a page from an existing site (portfolio re-do, redesign), scrape the DATA via browser but deliberately differentiate the DESIGN:

1. **Harvest data with `browser_console`, not screenshots.** `document.body.innerText` (slice for pagination) gets headings/paragraphs; `document.querySelectorAll('button[aria-expanded]')` + `.click()` opens accordions/cards to reveal hidden detail; `browser_get_images` lists assets to reuse (profile photos); `curl -o` pulls the asset binary.
2. **Inventory the source's design language before designing the replacement** so you can avoid it: note font stack, dark/light, gimmicks (marquee/ticker, terminal windows, numbered sections, table-as-ledger). Then pick a contrasting direction — e.g. source was dark-terminal IBM Plex → build light-editorial Source Serif + Inter on cream paper.
3. **Verify interactivity headless** when you can't see the page: drive filters/search/modal via `browser_console` (`element.click()`, dispatch `input` event, then count `.pcard` nodes, assert modal `classList.contains('open')`), plus image-load check (`img.complete && naturalWidth > 0`). Assert counts per state (filter Integration=2, search=2, empty state exists) — these catch broken JS without eyes.

## Environment: WSL + Windows PHP (Laragon)

- WSL has no PHP; Laragon's `php.exe` runs the app: `/mnt/c/laragon/bin/php/php-<ver>/php.exe artisan serve --host=0.0.0.0 --port=8899`.
- WSL2 is NAT'd: Windows `127.0.0.1` is NOT reachable from WSL. Access the server via the gateway IP: `GW=$(ip route show default | awk '{print $3}')` → `http://$GW:8899/` (bind `--host=0.0.0.0` or Windows firewall blocks it).
- Image processing without PIL/ImageMagick: use Laragon PHP GD (`imagecreatefromjpeg`, `imagecrop` center-square, `imagescale`) — see `scripts/circle-crop-resize.php`. `mkdir` the destination dir first; Windows PHP won't create it.

## Reference

- `references/implementation-pitfalls.md` — full detail: the fill-mode bug reproduction, audit expression walkthrough, WSL serve setup.
- `references/dark-mode-and-expand.md` — dark-mode token table + wiring, toggle JS, grid-rows disclosure markup, computed-style verification, bulk-rename substring bug.
- `references/premium-animation-recipe.md` — Pier88-style premium motion: Lenis smooth scroll + required CSS, blur-reveal, split-line headings, GSAP carousel, motion tiering, and the HTMLCollection/lerp-IO pitfalls.
