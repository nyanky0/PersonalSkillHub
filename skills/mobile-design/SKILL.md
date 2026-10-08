---
name: mobile-design
description: "Mobile-first responsive design, thumb-friendly touch targets, and adaptive layouts."
---

# Mobile Design — Worked With Web

Design and build web interfaces that feel native on mobile and scale up
gracefully to desktop. Mobile is the primary canvas, not an afterthought.

## 1. Mobile-First Strategy

- Write CSS **mobile-first**: base styles for small screens, then `@media (min-width: …)` to enhance upward. This keeps mobile CSS lean.
- Common breakpoints (Tailwind defaults are fine): `sm 640, md 768, lg 1024, xl 1280`.
- Test the primary user journey at 375px (iPhone SE/13), 390px (iPhone 14), and 768px (tablet) before anything else.
- Use `clamp()` for fluid type/spacing: `font-size: clamp(1.5rem, 4vw, 3rem)` — no jarring jumps.

## 2. Touch & Thumb Zone

- Touch targets ≥ **44×44px** (48px preferred). Never less than 40px.
- Put primary actions in the **thumb zone**: bottom half of the screen, or a bottom bar / floating action.
- Nav CTAs and menus reachable with one thumb — hamburger/menu at bottom-right or top-right is acceptable; avoid far-left critical controls.
- `active` feedback (scale/opacity) on all tappable elements.
- No hover-dependent functionality — hover doesn't exist on touch. Use `@media (hover: hover)` for hover-only enhancements.
- Keep tap-to-action distance ≥ 8px between touch targets.

## 3. Layout & Breakpoints

- **Single column** by default; grid only at `sm/md`+.
- Cards/features stack vertically on mobile (`grid-cols-1` → `sm:grid-cols-2` → `lg:grid-cols-3`).
- Tables → cards on mobile, or horizontal scroll with sticky first column.
- Images: `w-full h-auto`, use `srcset`/`sizes` for resolution; `object-fit: cover` for crops; consider `loading="lazy"` below the fold.
- Prevent horizontal overflow: `overflow-x: hidden` on body only as a last resort — fix the root cause (oversized fixed-width elements, long unbroken strings with `overflow-wrap: break-word`).
- **Safe areas:** respect notches — `env(safe-area-inset-bottom)` for sticky bottom bars, `viewport-fit=cover`.

## 4. Mobile Navigation

- Condense nav: icon-only top bar, bottom tab bar for apps, or hamburger → slide-in drawer (with backdrop, focus trap, ESC to close).
- Sticky header ≤ 56-64px tall; hide on scroll down, reveal on scroll up (optional but premium).
- Breadcrumbs collapse to back-arrow on mobile.

## 5. Performance (mobile = slow networks)

- Lazy-load images/videos; use `loading="lazy"` + `decoding="async"`.
- Minify/bundle assets; avoid shipping desktop-sized media to phones.
- Keep FCP/LCP small: inline critical CSS, preload hero font/image, avoid render-blocking JS.
- Use system fonts or subsetted webfonts where possible.
- 60fps interactions; prefer CSS `transform`/`opacity` animations, `will-change` sparingly.

## 6. Web-App / Native-Feel Patterns

- **Bottom sheets** for filters/actions (with drag handle, rounded top corners).
- **Sticky bottom CTA bar** for e-commerce / checkout on mobile.
- Pull-to-refresh where the platform supports it; else provide a refresh button.
- Inputs: `inputmode` and `type` set correctly (tel, email, number) so the right keyboard appears; `font-size ≥ 16px` on inputs to prevent iOS zoom.
- PWA: theme-color meta, apple-mobile-web-app-capable, 192/512 icons, safe-area insets.

## 7. Do / Don't

- DO: mobile-first CSS, 48px targets, thumb-zone CTAs, stacked layouts, lazy media, safe-area handling, fluid typography.
- DON'T: desktop-first with `max-width` overrides everywhere, 20px tappable links, hover-only menus, 3-column grids on 375px screens, unbroken text overflow, mandatory desktop-only features on mobile.

## Checklist (run before declaring responsive work done)

1. No horizontal scroll at 320px, 375px, 768px.
2. All interactive targets ≥ 44px, spaced ≥ 8px.
3. Primary journey usable one-handed (thumb test).
4. No hover-gated content; `active` feedback present.
5. Forms use correct `type`/`inputmode`; no iOS zoom.
6. Media responsive + lazy; safe-area respected.
7. Layout stacks correctly at every breakpoint with consistent spacing.

This skill composes with `imagegen-frontend-mobile` (mockup direction), `ui-ux-pro-max` (design intelligence), and `vercel-webdesign` (aesthetic language). Use them together for premium results.
