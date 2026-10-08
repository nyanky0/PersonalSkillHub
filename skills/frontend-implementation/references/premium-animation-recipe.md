# Premium Animation Recipe — Pier88-style

Deconstructed from pier88coast.com (Aug 2026): WordPress + GSAP 3.12.5 + Lenis. Notably NOT used: ScrollTrigger (scroll anims are IO-driven), SplitText (headings pre-split in HTML), parallax, page transitions. Three layered motion systems, all reproducible with vanilla CSS/JS + 2 CDN libs.

## 1. Blur-reveal (the signature cinematic look)

```css
[data-reveal]{
  --reveal-duration:.7s;
  --reveal-ease:cubic-bezier(.19,1,.22,1);
  --reveal-delay:0ms;
  opacity:0;filter:blur(5px);transform:translate3d(0,24px,0);
  transition:opacity var(--reveal-duration) var(--reveal-ease) var(--reveal-delay),
              filter var(--reveal-duration) var(--reveal-ease) var(--reveal-delay),
              transform var(--reveal-duration) var(--reveal-ease) var(--reveal-delay);
  will-change:opacity,filter,transform;
}
[data-reveal].is-revealed{opacity:1;filter:blur(0);transform:translate3d(0,0,0)}
```

- Trigger: IntersectionObserver `{threshold:0.18, rootMargin:'0px 0px -8%'}`, `unobserve` after trigger.
- Guard: no IO or `prefers-reduced-motion` → add revealed class immediately (never leave content hidden).
- Cascade via `--reveal-delay` per element; helper classes `.d1/.d2/.d3` = 80/160/240ms.
- Reduced-motion reset must include `filter:none` (not just opacity/transform) or elements stay blurred.

## 2. Split-line heading reveal

Headings PRE-SPLIT in HTML (Pier88 splits manually, not SplitText):

```html
<h2>
  <span class="split-line"><span class="line-inner">Nunggu mobil, <span class="hl">sambil santap</span></span></span>
  <span class="split-line"><span class="line-inner">gulai kambing <span class="script-word">andalan</span></span></span>
</h2>
```

```css
.split-line{display:block;overflow:hidden}
.split-line .line-inner{display:block;transform:translateY(110%);transition:transform .9s cubic-bezier(.19,1,.22,1)}
.split-line.in .line-inner{transform:translateY(0)}
.script-word{font-family:'Playfair Display',serif;font-style:italic;color:var(--brand-2);display:inline-block;transform:translateY(110%);transition:transform .9s cubic-bezier(.19,1,.22,1)}
.split-line.in .script-word{transform:translateY(0)}
```

`.in` added by IO threshold ~0.3. Reduced-motion: `transform:none` on `.line-inner` and `.script-word`.

## 3. Lenis smooth scroll

CDN: `https://unpkg.com/lenis@1.1.14/dist/lenis.min.js`

REQUIRED companion CSS (from Lenis docs — without it, Lenis fights `scroll-behavior:smooth` and native anchors):

```css
html.lenis,html.lenis body{height:auto}
.lenis.lenis-smooth{scroll-behavior:auto!important}
.lenis.lenis-smooth [data-lenis-prevent]{overscroll-behavior:contain}
.lenis.lenis-stopped{overflow:hidden}
```

Init:

```js
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let lenis = null;
if (!prefersReduced && typeof Lenis !== 'undefined') {
  lenis = new Lenis({
    duration: 1.15,
    easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // expo-out ≈ GSAP power3.out
    smoothWheel: true,
    touchMultiplier: 1.5,
  });
  function raf(time){ lenis.raf(time); requestAnimationFrame(raf); }
  requestAnimationFrame(raf);
}
```

Anchors: `lenis.scrollTo(el, {offset:-60, duration:1.2})` with `preventDefault` on `a[href^="#"]`. Skip init entirely under reduced motion.

## 4. GSAP carousel (slide + content stagger)

CDN: `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`

```js
function go(i) {
  i = (i + slides.length) % slides.length;
  if (i === current) return;
  gsap.killTweensOf(slides);
  const next = slides[i];
  gsap.set(next, { xPercent: 100, autoAlpha: 0 });
  gsap.to(slides[current], { xPercent: -100, autoAlpha: 0, duration: 0.46, ease: 'power3.out', overwrite: true });
  gsap.to(next, { xPercent: 0, autoAlpha: 1, duration: 0.46, ease: 'power3.out', overwrite: true });
  gsap.fromTo(next.querySelectorAll('.slide-body > *'),
    { autoAlpha: 0, y: 10, filter: useLowCostMotion ? 'none' : 'blur(2px)' },
    { autoAlpha: 1, y: 0, filter: 'none', duration: 0.46, stagger: 0.04, ease: 'power3.out', overwrite: true });
  current = i;
  // dots/counter update — see pitfall below
}
```

- `useLowCostMotion` = reduced-motion OR `matchMedia('(max-width:760px)')` → drop blur. Motion tiering.
- Auto-advance: `setInterval(next, 5000)`; reset (clear + restart) on every manual nav.

## Pitfalls (both hit in production)

1. **`dotsWrap.children.forEach` throws** — `.children` is HTMLCollection (no forEach). Exception lands AFTER the `gsap.to` calls but BEFORE `current = i` / dots / counter update → slides animate, indicators freeze, console floods with empty-message exceptions. Fix: `Array.from(dotsWrap.children).forEach(...)`. Debug signature: half-updated UI + burst of `{"message":"","source":"exception"}` in browser_console.
2. **Custom lerp scrollTo loop breaks IO reveals** — a rAF `window.scrollTo(0, cur)` lerp fires scroll events faster than IO can settle thresholds; reveal classes never add (stuck at e.g. 3/11). Lenis does NOT have this problem (drives `transform` on a wrapper). If not using Lenis, use native `scroll-behavior: smooth`.

## 5. Parallax = scroll → CSS vars (exact Pier88 code)

Deconstructed from Pier88's plate-journey + coastal-table hero. NO parallax library, NO ScrollTrigger — plain rAF + CSS custom properties. Element and background move OPPOSITE directions = depth.

```js
(function () {
  const hero = document.querySelector('.hero');
  const plate = document.querySelector('.hero-plate');      // floating element
  const bg = document.querySelector('.hero-bg-par');        // background wrapper
  if (!hero || !plate || !bg || prefersReduced) return;
  let ticking = false;
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const easeInSine = t => 1 - Math.cos((t * Math.PI) / 2);

  function updateParallax() {
    const rect = hero.getBoundingClientRect();
    const vh = window.innerHeight || document.documentElement.clientHeight;
    // background: drifts as section crosses viewport center
    const centerOffset = (rect.top + rect.height / 2 - vh / 2) / vh;
    bg.style.setProperty('--bg-y', `${centerOffset * 46}px`);
    // floating element: exits downward proportional to scroll, eased
    const exitStart = vh * 0.12;
    const exitDistance = vh * 0.88;
    const exitProgress = easeInSine(clamp((-rect.top - exitStart) / exitDistance, 0, 1));
    const exitY = exitProgress * (plate.offsetHeight + 32);
    plate.style.setProperty('--plate-y', `${exitY}px`);
    ticking = false;
  }
  const requestUpdate = () => {
    if (!ticking) { window.requestAnimationFrame(updateParallax); ticking = true; }
  };
  updateParallax();
  window.addEventListener('scroll', requestUpdate, { passive: true });
  window.addEventListener('resize', requestUpdate);
})();
```

```css
.hero-bg-par{ position:absolute; inset:-6%; width:112%; height:112%;
  transform:translateY(var(--bg-y,0)); will-change:transform; }
.hero-plate{ position:absolute; z-index:2; right:8%; bottom:-8%;
  transform:translateY(var(--plate-y,0)); will-change:transform; }
```

Key points:
- **`ticking` guard** — one rAF per frame even with many scroll events; `passive:true`.
- **`inset:-6%` on the bg wrapper** — translateY would expose the top/bottom edges without overscan.
- Reduced-motion: `transform:none !important` on both, and skip the whole IIFE.

## 6. Sticky-pin scroll section ("plate journey" feel)

Container `position:relative` with a TALL height; inner `position:sticky`; scroll progress over the tall container drives element transforms (often combined with §5). Pier88: `.p88-plate-journey{position:relative; height:5200px}` + `.p88-plate-journey__pin{position:sticky}`. Drift elements pre-positioned via GSAP `translate(0, 400px)` outside viewport, animated in by scroll.

## 7. Carousel init (all slides stacked bug)

```js
// hide all but the first slide at init, or every slide is visible stacked
// until the first auto-advance fires (5s) — looks broken on load
gsap.set(slides.slice(1), { xPercent: 100, autoAlpha: 0 });
```

## 8. Vanilla slider (no GSAP) — absolute anchoring, not flex

When GSAP CDN fails to load on the user's browser (or you want zero deps), the vanilla fallback still must handle positioning correctly:

```css
.slider{ position:relative; overflow:hidden; min-height:300px; } /* min-height! absolute children collapse it */
.slide{ position:absolute; inset:0; transition: transform .5s cubic-bezier(.19,1,.22,1), opacity .5s ease; }
```

```js
function apply(){
  slides.forEach((s, i) => {
    const off = i - current;
    s.style.transform = `translateX(${off * 100}%)`;
    s.style.opacity = off === 0 ? '1' : '0';
    s.style.pointerEvents = off === 0 ? 'auto' : 'none';
  });
}
```

- **flex + translateX trap**: in `display:flex`, `translateX(100%)` offsets relative to each slide's flex slot → the active slide ends up at `left: sliderLeft + width` (offscreen). Absolute `inset:0` anchors every slide at the slider box, so translateX is relative to the slider and the active slide is always centered. Verified failure: slide 2 active at `left:1168` while slider at `left:97` = blank; after absolute fix, active slide always at `left:98`.
- **`loading="eager"` on all slider imgs** — lazy + translated offscreen = browser never fetches → blank slide when it becomes active. Add `decoding="async"`.
- **Auto-play `setInterval` makes test assertions flaky** — between click and assert the timer advances. Assert within one tick, or click-dot-3 → check → click-dot-0, accepting drift; or disable timer in test.
- Keep transition on `transform`/`opacity` only.

## Design lesson: floating decorative elements

Pier88's drifting plate reads premium because it's INTEGRATED into its scene (plate photo on a seaside table, part of the section artwork). A random food photo floating in a hero (decorative `<img>` + parallax exit) reads as broken/ugly to the user — "aneh, masa ada gambar gulai kambing yang ngikutin turun". Rule: floating parallax elements must look like they belong to the scene (same palette, framed, edge-faded, small, contextual) — or drop them. Parallax on the BACKGROUND wrapper alone (opposite-direction drift) already delivers the depth feel.

## Verification checklist (headless, no vision)

- Reveal state: initial `getComputedStyle(el).filter === 'blur(6px)'` + opacity 0 → after full scroll `blur(0px)` + opacity 1, count `'.reveal.in'` == total.
- Split-lines: `'.split-line.in'` == total after scroll to bottom (wait ~1.4s — transitions + IO both async).
- Lenis: `document.documentElement.classList.contains('lenis')`, and `window.scrollY` still updates (transform-based, not scrollTo).
- Slider: click next/prev/dot → counter text + `.sdot.active` index + slide transforms all agree.
- Fresh-error trap: `browser_console clear=true` only clears the buffer; accumulated exceptions from BEFORE the fix still replay. Arm `window.addEventListener('error', ...)` AFTER reload, then interact, then read — distinguishes stale from fresh.
