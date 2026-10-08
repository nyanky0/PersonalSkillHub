# Implementation Pitfalls — Full Detail

Session-derived detail behind the frontend-implementation SKILL.md. Verified on a Laravel 12 + Tailwind 4 + Vite 8 + Laragon (Windows PHP) landing-page build.

## 1. Tailwind 4 rebuild trap (wasted ~10 min)

Adding `h-28 w-28 lg:h-44 lg:w-44 object-cover` to an `<img>` produced a 512×512 rendered image (natural size) instead of 176px. `rounded-full` (already used elsewhere) applied; the NEW size classes did not.

Root cause: Tailwind 4 generates CSS by scanning source files at build time. Classes never used before are absent from the built CSS until `npm run build`. `@tailwindcss/vite` in dev mode normally picks this up, but when assets are served from `public/build` (built manifest), a rebuild is mandatory.

Rule: **rebuild after every edit introducing a never-before-used utility class.** Cheap way to confirm: check `getComputedStyle(el).height` in the browser — if it matches the Tailwind value, class is live.

## 2. `animation-fill-mode: both` kills hover transforms

Hero elements used `@utility hero-fade { animation: hero-fade 0.6s ease-out both; }` where `to { opacity:1; transform:none }`. Adding `:hover { transform: scale(1.02) }` to the same image did nothing — computed transform stayed `none` after load.

Why: `fill-mode: both` (like `forwards`) keeps applying the last keyframe's values forever. The animation's `transform: none` outranks the hover rule (animations beat normal declarations in the cascade). `getAnimations()` showed a finished animation still holding.

Fix: `animation: hero-fade 0.6s ease-out backwards;` — `backwards` applies the `from` state during the delay (so elements don't flash) but RELEASES after finishing, letting transitions/hover take over. Verified: `img.getAnimations()` → `[]` after load, hover scale works.

General rule: elements that need hover/transition transforms must not have a held animation on `transform`. Either use `backwards`, or keep the animation to `opacity` only.

## 3. Progressive-enhancement scroll reveal

```js
document.documentElement.classList.add('js'); // app.js top
```
```css
.js .reveal { opacity: 0; transform: translateY(16px); transition: opacity .7s ease, transform .7s ease; }
.js .reveal.is-visible { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .js .reveal { opacity: 1; transform: none; transition: none; } }
```
- Hidden state only exists under `.js` — no-JS users get content immediately (no invisible-content flash, no empty page when JS fails).
- IntersectionObserver adds `.is-visible` once, then `unobserve`s. Fallback: no observer support → add `.is-visible` to everything.
- Stagger: `style="--d: {{ $i * 45 }}ms"` + `transition-delay: var(--d)`. Ledger rows at 45ms each; stats at 70ms; cap ~300ms.
- Count-up counters: same observer pattern, `data-count`/`data-decimals`, rAF + ease-out-cubic over ~1.1s, final value instantly under reduced motion. Put the final value in `aria-label` on the container so screen readers get the resolved number.

## 4. WSL2 + Laragon PHP serve (no PHP in WSL)

- WSL shell has no `php`. Laragon ships one: `/mnt/c/laragon/bin/php/php-8.3.30-Win32-vs16-x64/php.exe`.
- `php artisan serve` binds 127.0.0.1 on the WINDOWS side. WSL2 is NAT'd — Windows loopback is unreachable from WSL and vice versa. `curl http://127.0.0.1:8899` from WSL → 000.
- Fix: bind `--host=0.0.0.0 --port=8899`, then from WSL reach it at the gateway IP: `GW=$(ip route show default | awk '{print $3}')` → `http://$GW:8899/`. Windows users keep using `http://127.0.0.1:8899/`.
- Server died once with exit 255 (backgrounded artisan serve under a Windows process) — restart is trivial; always `curl` health-check before blaming the page.

## 5. PHP GD image processing (no PIL/ImageMagick)

Resize + center-crop square avatar with Laragon's php.exe:

```php
$img = imagecreatefromjpeg($src);
$size = min(imagesx($img), imagesy($img));
$sq = imagecrop($img, ['x' => (int)((imagesx($img)-$size)/2), 'y' => (int)((imagesy($img)-$size)/2), 'width' => $size, 'height' => $size]);
imagejpeg(imagescale($sq, 512, 512), $dst, 85);
```

Pitfalls: Windows PHP does NOT create missing directories — `mkdir -p public/images` first or `imagejpeg` fails with "Failed to open stream". Script was a throwaway file deleted after use.

## 6. Headless verification without vision provider

Vision failed (`No LLM provider configured for task=vision`), so verification was a `browser_console` computed-style audit. Keys:

- Fonts: `document.fonts.check('16px "IBM Plex Sans"')` — confirms @font-face actually loaded.
- Layout: `getBoundingClientRect()` width/height vs expected; `document.body.scrollWidth - window.innerWidth` for horizontal overflow (negative = fine; scrollbar subtracts ~15px).
- Animation release: `el.getAnimations().map(a => a.playState)` — empty array after load proves fill-mode released.
- Broken-class detection: `getComputedStyle(el).height` mismatch with the utility's expected value = class not in built CSS (see #1).
- `window.resizeTo()` is silently ignored in headless browsers — verify responsive behavior by checking breakpoint classes/`display:none` rules in the CSS, not by resizing.

## 7. Mobile menu + sticky masthead (accessibility)

Hamburger toggle must be a `<button>` with `aria-expanded`, `aria-controls`, dynamic `aria-label` (Open/Close menu), Escape-to-close with focus return, close-on-link-tap, and auto-reset on resize past the breakpoint. Panel hidden via `.mobile-menu { display:none }` + `.open { display:block }`. Icon swap hamburger↔X via two SVGs toggling a `hidden` class. `scroll-mt-24` on anchored sections offsets the sticky 48px header.

## 8. Browser-tool stale DOM snapshot (trap) — added 2026-08-14

2026-08-14 session: after editing `index.html` and redeploying to GitHub Pages, `browser_navigate` / `browser_snapshot` and `browser_console` kept returning the OLD DOM (title "Maul — Fullstack Developer", 0 project cards with group border) even after `Ctrl+F5`. Root cause: the browser tool serves from a cached snapshot, not a live reload — `curl` proved the new file was live (title "Maul — CLI", `#0d1117`, 3 project cards) while the browser tool did NOT reflect it.

**Rule:** never trust browser-tool DOM snapshots after a rapid edit+redeploy. Confirm via raw HTTP instead:

```bash
curl -s https://muhamadmaulanarizki.github.io/portfoliodemo/ | grep -oE '<title>[^<]+'
```

This catches whether the latest file is actually live, decoupled from the browser-tool cache. Use browser_console computed-style ONLY after `curl` confirms the right version is served — and re-run `curl` if console values look stale.

## 9. Blade comments / raw-output tags leak into plain HTML

When copying Blade markup (`{!-- --}` comments, `{!! !!}` raw-output tags, `{!!--- ---}!!`) into a standalone `.html` file served from GitHub Pages / Vercel, they render verbatim as visible text instead of being stripped. Checklist post-rewrite:

```bash
grep -nE '\{!/|\{!--|\{\!/|\{//' index.html   # must return nothing
```

Replace with standard `<!-- -->` comments. Also confirm no Blade variables `{{ $var }}` survive — static HTML has no engine to interpolate them.
