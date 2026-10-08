---
name: web-animation
description: "Web animation: easing, timing, performant motion patterns."
version: 1.0.0
author: Hermes Agent (synthesized from Josh W. Comeau, animations.dev)
license: MIT
platforms: [linux, macos, windows, wsl]
triggers:
  - add animation to website
  - css transition / animation
  - easing curve
  - hover micro-interaction
  - scroll reveal animation
  - web animation performance
  - prefers-reduced-motion
---

# Web Animation

Synthesis of Josh W. Comeau's "Interactive Guide to CSS Transitions" + animations.dev (Emil Kowalski) + frontend-design skill. Goal: craft animations that feel right, not just "work". Easing & timing matter more than technique.

## Core principles

1. **Motion is salt** — too much spoils the dish. Be precise with which properties animate. An orchestrated moment lands harder than scattered effects.
2. **Good animations mimic the natural world** — nothing real moves linearly. Pick organic timing.
3. **Think in actions, not states** — animate based on what the user is doing (mouse-enter vs mouse-leave), each with its own duration/easing.
4. **Test on the lowest-end device** you target. Your dev machine is many times faster.

## The CSS transition workhorse

```css
.btn { transition: transform 250ms; }
.btn:hover { transform: translateY(-10px); }
```

- Two required values: property + duration. Comma-list for multiple: `transition: transform 250ms, opacity 400ms;`
- **Never use `transition: all`** — an unexpected animation slips through as the product evolves.

## Timing functions — when to use what

| Function | Curve | Use for |
|---|---|---|
| `linear` | constant | Almost never. Nothing real moves this way. |
| `ease-out` | fast start, sleepy end | **Entering** viewport: modal appearing, element sliding in. Charging in, settles. |
| `ease-in` | slow start, speeds up | **Exiting** viewport (moving off-screen/invisible). Sudden stop is jarring otherwise. |
| `ease-in-out` | symmetrical | Loops — element fading in/out repeatedly. |
| `ease` (default) | brief ramp-up + lots of deceleration | **Most cases** — element moves but isn't entering/exiting. |

- Time is constant: timing functions describe how a value gets from 0→1 over a fixed interval, not how fast the animation completes.
- Custom curves: `cubic-bezier(0.1, 0.2, 0.3, 0.4)` — 4 numbers = 2 control points. Use an easing wizard (easingwizard.com) to preview, then paste.

## Performance — the critical bits

- 60fps = 16.6ms per frame. Expensive animations drop frames → jank.
- **Expensive**: `height`, `width`, `left`, `top` (affect layout → chain reaction on siblings), `background-color` (repaint every frame).
- **Cheap**: `transform` + `opacity` — GPU-composited, no layout/paint.
- Rule: if you're animating `width`/`left`, move it to `transform` (translate/scale).
- `margin-top` can't sub-pixel-render → stepped jank. `transform` smooths between pixels via GPU anti-aliasing.

## Hardware acceleration & will-change

- Browser hands `transform`/`opacity` animations to GPU as a texture → slick 60fps. Known as hardware acceleration.
- CPU↔GPU hand-off causes a telltale "snap" at animation start/end (text glitches slightly).
- Fix: `will-change: transform;` on the animated element — GPU handles it always, no hand-off snap.
- Tradeoff: consumes video memory. **Don't apply will-change broadly** to elements that won't move. Be intentional.
- Legacy trick: `transform: translateZ(0px)` (3D transform forces GPU). `will-change` is the modern, semantic way. Differences still exist in niche cases — test on target devices.

## UX touches — action-driven motion

### Asymmetric hover (enter fast, exit relaxed)

```css
.btn {
  will-change: transform;
  transition: transform 450ms;   /* exit: relaxed */
}
.btn:hover {
  transition: transform 125ms;   /* enter: snappy */
  transform: translateY(-10px);
}
```

### Modal enter/exit

Enter with `ease-out` (hustle in, settle). Exit with quicker `ease-in` (leave fast, invisible).

### Transition-delay saves dropdowns

Hover dropdown closes when cursor dips out-of-bounds while moving to a child. Fix without JS:

```css
.dropdown {
  opacity: 0;
  transition: opacity 400ms;
  transition-delay: 300ms;          /* grace period before closing */
}
.dropdown-wrapper:hover .dropdown {
  opacity: 1;
  transition: opacity 100ms;
  transition-delay: 0ms;
}
```

Shorthand: `transition: opacity 250ms 300ms;` (duration then delay).

### Doom flicker

Moving an element on hover takes it out from under the mouse → falls back → hover retriggers → flicker loop (can trigger photosensitive epilepsy). **Fix: separate trigger from effect** — animate a child element, keep the trigger stationary:

```html
<button class="btn"><span class="background">Hello World</span></button>
```

```css
.btn:hover .background {
  transition: transform 150ms;
  transform: translateY(-10px);
}
```

The `<button>` itself never moves; the child peeks out above it.

## Respect motion preferences (mandatory)

```css
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
```

Some users get nausea/malaise from motion. This is a responsibility, not a nice-to-have.

## Practical pattern set (from real sites)

- **Scroll reveal**: IntersectionObserver → add class → `opacity 0→1` + `translateY(20px→0)` with `ease-out` ~500ms. Unobserve after trigger (once).
- **Stagger**: sibling `animation-delay: calc(i * 30ms)` capped (~240ms) so the last item doesn't lag.
- **Hover card lift**: `transform: translateY(-2px)` + border/shadow, 150ms, `ease-out` — subtle beats dramatic.
- **Entrance of modal/dialog**: scale `0.97→1` + `translateY(6px→0)`, 180ms `ease-out`, opacity fade. Exit: 120ms `ease-in`.
- **Live feedback**: status dot breathing (`scale 1→1.18` loop, `ease-in-out` — loops want symmetrical curves).
- **Accordion/expand**: animate `height` → but `height` is expensive. Prefer `grid-template-rows: 0fr→1fr` trick or `max-height` with generous value.

## Pitfalls

- `transition: all` — precision over convenience; an accidental animation slips in later.
- `linear` everywhere — makes UI feel robotic/3D-printer-like.
- `ease-in` for entrances — ends with jarring stop; entrances want `ease-out`.
- `will-change` on everything — burns video memory on mobile.
- `height`/`width` animation — layout thrash; use transform or grid-rows trick.
- Scroll reveal without reduced-motion guard — motion-sick users get full-page animation.
- Animating `left`/`top` for position — use `transform: translate` instead (GPU path).

## Verification

1. `node --check` extracted JS (if any) for syntax errors.
2. Browser: console 0 errors; check `prefers-reduced-motion` media query works (DevTools emulation).
3. Visual: hover states, modal open/close, scroll reveals — all smooth (no snap/jank).
4. Performance: DevTools Performance tab — no long frames; only transform/opacity in the animation.
