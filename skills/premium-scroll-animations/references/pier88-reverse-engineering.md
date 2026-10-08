# Pier88 Coast — reverse-engineered animation details

Source: pier88coast.com (live analysis, WordPress + GSAP 3.12.5 + Lenis, no ScrollTrigger, no SplitText, no barba, no parallax lib).

## Stack detection signals (how to identify on any site)

- `script[src]` names: `gsap.min.js`, `lenis.min.js`, `lottie.min.js` → GSAP + Lenis + Lottie.
- `typeof window.ScrollTrigger === 'undefined'` despite heavy scroll animation → scroll anim is NOT ScrollTrigger; driven by IO + rAF + CSS vars instead.
- Heading spans with `translate: none; rotate: none; scale: none; transform: ...` inline styles → GSAP-set transforms (gsap.set/fromTo).
- Reveal via class toggle: `[data-p88-reveal]` default `opacity:0; filter:blur(5px); translate3d(0,24px,0)`, `.is-p88-revealed` → `opacity:1; filter:blur(0); translate3d(0,0,0)`. IO `threshold:0.18, rootMargin:"0px 0px -8%"`, unobserve on trigger. Guard: no-IO or reduced-motion → add class immediately.
- Section heights: `p88-plate-journey` height 5200px + inner `__pin` sticky → long-pin scroll scene.

## Exact GSAP carousel code (food/event sliders)

```js
gsap.killTweensOf(contentItems);
gsap.fromTo(contentItems,
  { autoAlpha: 0, y: 10, filter: useLowCostMotion ? "none" : "blur(2px)" },
  { autoAlpha: 1, y: 0, filter: "none", duration: 0.46, stagger: 0.04, ease: "power3.out", overwrite: true }
);
```

## Exact parallax code (hero plate + background)

```js
// plate: exits downward proportional to scroll progress
const exitStart = isMobileHero ? viewportHeight * 0.04 : viewportHeight * 0.12;
const exitDistance = isMobileHero ? viewportHeight * 0.96 : viewportHeight * 0.88;
const exitProgress = easeInSine(clamp((-rect.top - exitStart) / exitDistance, 0, 1));
const exitY = exitProgress * ((isMobileHero ? viewportHeight : plate.offsetHeight) + 32);
section.style.setProperty("--coastal-plate-exit-y", `${exitY}px`);
plate.style.visibility = isNearSection ? "visible" : "hidden";

// background: drifts opposite, scaled by section center offset
const centerOffset = (rect.top + rect.height / 2 - viewportHeight / 2) / viewportHeight;
section.style.setProperty("--coastal-bg-y", `${centerOffset * 46}px`);

// rAF guard
const requestUpdate = () => { if (!ticking) { window.requestAnimationFrame(updateParallax); ticking = true; } };
window.addEventListener("scroll", requestUpdate, { passive: true });
window.addEventListener("resize", requestUpdate);
```

## Other notable details

- `p88-light-wash` span injected into section targets (`coastal-table-section`, `p88-coastal-atmosphere`, `p88-drinks-experience`, `p88-day-night`, `p88-waves-cta__pin`) — light overlay.
- Hero: video `Blue-Waters.mp4` autoplay muted loop playsinline + poster webp. Ken Burns substitute for stills: `scale(1→1.08)` 22s ease-in-out alternate.
- Sections with full-bg image: `coastal-table-section`, `p88-coastal-atmosphere` — `background-size:cover; background-attachment:scroll` (NOT fixed).
- Glass header: scroll listener + rAF `updateGlass()` toggling `setState(true/false)` on threshold.
- Reduced-motion handled per-animation (`matchMedia("(prefers-reduced-motion: reduce)")` → skip / static state).

## Session context (SP IK G landing, spikg-landing.html)

Applied stack: Lenis 1.1.14 + blur-reveal (6px) + 11 split-lines + Playfair italic script words + vanilla absolute-slider carousel + rAF bg parallax (46px scale) + 2 full-bleed bg-bands + Ken Burns hero. All verified via browser console probes. User-requested removals: prices, hero floating plate (scene mismatch), GSAP dependency (vanilla slider instead).
