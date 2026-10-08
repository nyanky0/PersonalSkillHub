# Pier88 Coast teardown — premium motion patterns

Source: https://pier88coast.com (analyzed live via browser console, Aug 2026).
Stack: WordPress + GSAP 3.12.5 + Lenis 1.1.14 + vanilla JS. **No ScrollTrigger, no SplitText, no parallax lib** — everything is IntersectionObserver + CSS transitions + rAF scroll handlers. The premium feel is timing + blur + layering, not the library.

## What the site does NOT use (learned by probing)

- `ScrollTrigger` NOT registered (checked `window.gsap.plugins` — only core css/attr/endArray/roundProps/modifiers/snap). Scroll animation = IntersectionObserver + Lenis scroll callbacks, not GSAP scroll.
- No SplitText — split headings are hand-written per-line spans in HTML.
- No barba/page transitions, no parallax library.

## 1. Reveal system (all sections)

```css
html.p88-polish-ready [data-p88-reveal] {
  opacity: 0; filter: blur(5px); transform: translate3d(0, 24px, 0);
  transition:
    opacity var(--p88-reveal-duration) var(--p88-editorial-ease),
    filter var(--p88-reveal-duration) var(--p88-editorial-ease),
    transform var(--p88-reveal-duration) var(--p88-editorial-ease);
  transition-delay: var(--p88-reveal-delay, 0ms);
  will-change: opacity, filter, transform;
}
html.p88-polish-ready [data-p88-reveal].is-p88-revealed {
  opacity: 1; filter: blur(0); transform: translate3d(0, 0, 0);
}
```

```js
// guard: no-IO or reduced-motion → reveal everything instantly
if (!elements.length || reduceMotion || !("IntersectionObserver" in window)) {
  elements.forEach(el => el.classList.add("is-p88-revealed"));
  return;
}
document.documentElement.classList.add("p88-polish-ready");  // gates the hidden state
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add("is-p88-revealed");
    observer.unobserve(entry.target);
  });
}, { threshold: 0.18, rootMargin: "0px 0px -8%" });
```

Key details:
- `html.p88-polish-ready` gate: hidden state only applies after JS confirms IO works. Without it, no-JS users would get permanently hidden content.
- `rootMargin: -8%` — element must pass 8% up into the viewport before revealing.
- CSS custom properties for duration/ease/delay → one knob per site, consistent everywhere.

## 2. GSAP usage — exactly 3 places (not everything)

### a) Carousel slide transition (the recipe)

```js
gsap.killTweensOf(contentItems);
gsap.fromTo(contentItems,
  { autoAlpha: 0, y: 10, filter: useLowCostMotion ? "none" : "blur(2px)" },
  { autoAlpha: 1, y: 0, filter: "none", duration: 0.46, stagger: 0.04, ease: "power3.out", overwrite: true });
```

- 0.46s + stagger 0.04 + power3.out = the feel.
- `useLowCostMotion` tiering: disable blur filter on mobile/reduced-motion.

### b) Hero — `matchMedia("(max-width: 760px)")` branch for mobile vs desktop positioning.

### c) Ambient float — CSS keyframes `p88-float-soft 9s ease-in-out infinite` on icons/leaves (CSS, not GSAP).

## 3. Scroll parallax WITHOUT ScrollTrigger (the "piring bergerak" effect)

### Background drift

```js
const centerOffset = (rect.top + rect.height / 2 - viewportHeight / 2) / viewportHeight;
section.style.setProperty("--coastal-bg-y", `${centerOffset * 46}px`);
```

Background translates by `var(--coastal-bg-y)` — drifts slowly, opposite direction to content = depth. 46px is the max travel (small, subtle).

### Plate exit (element drifting down as you scroll)

```js
const exitStart = isMobileHero ? viewportHeight * 0.04 : viewportHeight * 0.12;
const exitDistance = isMobileHero ? viewportHeight * 0.96 : viewportHeight * 0.88;
const exitProgress = easeInSine(clamp((-rect.top - exitStart) / exitDistance, 0, 1));
const exitY = exitProgress * ((isMobileHero ? viewportHeight : plate.offsetHeight) + 32);
section.style.setProperty("--coastal-plate-exit-y", `${exitY}px`);
plate.style.visibility = isNearSection ? "visible" : "hidden";
```

- `easeInSine = t => 1 - Math.cos((t * Math.PI) / 2)` — slow start, accelerates as you scroll away.
- `visibility: hidden` when section off-screen (perf).
- Plate is INSIDE the hero scene (photo of plate on table) — that's why its motion reads natural. A random product photo floating over unrelated content reads broken.

### Pinned drift section (`p88-plate-journey`)

```css
.p88-plate-journey { position: relative; height: 5200px; }   /* long scroll runway */
.p88-plate-journey__pin { position: sticky; top: 0; }         /* pins to viewport */
```

- Container `height ~5200px` → inner `position: sticky` → as you scroll the 5200px, the sticky pin stays in view.
- Drift children (`__drift-image`, `__drift-icon`) get inline `transform: translate(0px, 403.9px)` updated per scroll — 11 elements at different offsets = parallax depth within the pinned scene.
- Scroll handler: rAF + `ticking` guard, `passive: true`.

## 4. Split-line heading (hand-written, no SplitText)

```html
<span class="split-line"><span class="line-inner">FRESH</span></span>
<span class="split-line"><span class="line-inner">seafood <em>Italian Ease</em></span></span>
```

```css
.split-line { display: block; overflow: hidden; }
.split-line .line-inner {
  display: block; transform: translateY(110%);
  transition: transform .9s cubic-bezier(.19, 1, .22, 1);
}
.split-line.in .line-inner { transform: translateY(0); }
```

- Per-line (not per-word) masking: `overflow:hidden` parent clips, line slides up out of its own mask. `cubic-bezier(.19,1,.22,1)` = expo-out — the premium ease.
- Script accent word mid-line: `font-style: italic` in a serif display face (`Playfair Display` in the SP IK G port) — same reveal, distinct color.

## 5. Section interleaving (background rhythm)

- Full-bleed bg-image sections (`background-size: cover; background-attachment: scroll`) interleaved between text sections — the scroll rhythm alternates "scene / text / scene / text". `background-attachment: scroll` (NOT fixed) → smooth on mobile.
- Hero video: `autoplay muted loop playsinline poster` — poster webp covers slow loads.

## 6. Lenis smooth scroll — correct setup

```html
<script src="https://unpkg.com/lenis@1.1.14/dist/lenis.min.js"></script>
```

```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-smooth [data-lenis-prevent] { overscroll-behavior: contain; }
.lenis.lenis-stopped { overflow: hidden; }
```

```js
const lenis = new Lenis({ duration: 1.15, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);
// anchor links:
lenis.scrollTo(el, { offset: -60, duration: 1.2 });
```

- Guard: skip `new Lenis()` under `prefers-reduced-motion`.
- **Lenis does NOT break IntersectionObserver** (it scrolls natively). A custom `window.scrollTo` lerp loop DOES — IO never fires mid-loop. Use Lenis or native `scroll-behavior: smooth`, never a manual scrollTo rAF loop alongside IO reveals.

## 7. Bugs found while porting (SP IK G landing)

- `dotsWrap.children.forEach` — `children` is HTMLCollection, NOT array, no `.forEach` (NodeList has it). `TypeError` mid-`go()` → `current` never updates → counter/dots stuck while slides still move (gsap.to already ran). Fix: `Array.from(dotsWrap.children).forEach(...)`.
- Carousel init MUST hide non-active slides (`gsap.set(slides.slice(1), { xPercent: 100, autoAlpha: 0 })`) — otherwise all slides stack visible until first transition fires.
- GSAP from CDN can fail to load for the user → carousel dead, only slide 1 visible. Rewrote as vanilla: `translateX(off * 100%)` + CSS transition `cubic-bezier(.19,1,.22,1)` — no dep, same feel, survives CDN failure.
- Ken Burns animation + parallax both set `transform` on the same element → conflict. Fix: parallax on a wrapper (`inset: -6%` so translateY doesn't show edges), Ken Burns on the inner img.
