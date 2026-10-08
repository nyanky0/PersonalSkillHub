---
name: premium-scroll-animations
description: "Scroll animations: Lenis, blur-reveal, split-line, parallax."
version: 1.0.0
author: Hermes Agent (reverse-engineered from pier88coast.com)
license: MIT
platforms: [linux, macos, windows, wsl]
triggers:
  - smooth scroll / Lenis / inertia scroll
  - blur reveal on scroll
  - split-line heading reveal
  - scroll parallax (element + background)
  - hero video / Ken Burns background
  - carousel/slider animation
  - "make it look like pier88"
  - premium restaurant landing page animation
---

# Premium Scroll Animations

Reverse-engineered from pier88coast.com (GSAP 3.12.5 + Lenis + vanilla JS, no ScrollTrigger). The stack that makes premium sites feel expensive — plus the bugs that bite when replicating it. Full original code + detection signals: `references/pier88-reverse-engineering.md`.

## The 7-piece stack

1. **Lenis smooth scroll** — CDN `https://unpkg.com/lenis@1.1.14/dist/lenis.min.js`. Config: `duration 1.15`, `easing: t => Math.min(1, 1.001 - Math.pow(2, -10*t))` (expo-out), `smoothWheel: true`, `touchMultiplier: 1.5`. Drive with rAF loop. Skip init when `prefers-reduced-motion`. Anchor links via `lenis.scrollTo(el, {offset:-60, duration:1.2})`. Needs Lenis CSS:
```css
html.lenis, html.lenis body { height:auto; }
.lenis.lenis-smooth { scroll-behavior:auto !important; }
.lenis.lenis-smooth [data-lenis-prevent] { overscroll-behavior:contain; }
.lenis.lenis-stopped { overflow:hidden; }
```

2. **Blur-reveal** (signature: not plain fade) — `.reveal { opacity:0; filter:blur(6px); translate3d(0,24px,0); transition: opacity/filter/transform var(--reveal-duration) var(--reveal-ease) var(--reveal-delay); will-change:opacity,filter,transform; }` with `--reveal-duration:.7s; --reveal-ease:cubic-bezier(.19,1,.22,1)`. IO `threshold:0.12`, unobserve after trigger. Reduced-motion: `filter:none` reset too (else stuck blur).

3. **Split-line headings** — per line: `.split-line { display:block; overflow:hidden; }` + `.line-inner { display:block; transform:translateY(110%); transition:transform .9s cubic-bezier(.19,1,.22,1); }` `.split-line.in .line-inner { transform:translateY(0); }`. IO `threshold:0.3`. Accent word = script italic font (Playfair Display) inline in the line, same reveal.

4. **Carousel** — two options:
   - **Vanilla (no dep)**: slides `position:absolute; inset:0` inside `position:relative` slider (min-height set), `transform:translateX(off*100%)` + opacity, transition `cubic-bezier(.19,1,.22,1)` 0.5s. Counter `01/03`, dots, 5s auto-advance.
   - **GSAP**: `gsap.to(old,{xPercent:-100,autoAlpha:0,duration:0.46,ease:'power3.out'})`, `gsap.fromTo(newContent,{autoAlpha:0,y:10,filter:blur(2px)},{autoAlpha:1,y:0,stagger:0.04,duration:0.46,ease:'power3.out'})`. Low-cost tiering: drop blur on mobile/reduced-motion.

5. **Scroll parallax (rAF + CSS vars, no ScrollTrigger)**:
```js
let ticking = false;
function update() {
  const rect = section.getBoundingClientRect();
  const vh = window.innerHeight;
  const centerOffset = (rect.top + rect.height/2 - vh/2) / vh;
  section.style.setProperty('--bg-y', `${centerOffset * 46}px`);
  ticking = false;
}
const requestUpdate = () => { if (!ticking) { requestAnimationFrame(update); ticking = true; } };
window.addEventListener('scroll', requestUpdate, { passive:true });
window.addEventListener('resize', requestUpdate);
```
CSS: background layer in an **inset wrapper** (`position:absolute; inset:-6%; width:112%; height:112%; transform:translateY(var(--bg-y))`) so translate never shows edges. Opposite-direction layers (bg up, element down) = depth.

6. **Full-bleed bg-band sections** interleaved between text sections — `min-height:52vh; background-size:cover; background-position:center; background-attachment:scroll;` (NOT fixed — fixed is janky on mobile), shade gradient overlay, centered caption. The text→scene→text rhythm is most of the premium feel.

7. **Ken Burns hero** — `animation: kenburns 22s ease-in-out infinite alternate;` `scale(1→1.08)`, transform-only. Put on a DIFFERENT element than the parallax wrapper — CSS animation transform and inline parallax transform on the same element fight each other.

## Three more cheap premium micro-interactions (proven, layer cleanly onto the 7-piece stack)

8. **Scroll progress bar** — fixed 2px gradient line under the topbar that fills 0→100%. CSS: `.scroll-progress{position:fixed;top:0;left:0;height:2px;width:0;z-index:70;background:linear-gradient(90deg,var(--brand),var(--brand-2));will-change:width}`. JS rAF updates `bar.style.width = (scrollY/(scrollHeight-innerHeight))*100 + '%'`. Skip init on reduced-motion. Must live inside the main inline script (see "wrong `</script>` target" pitfall).

9. **Image curtain reveal (clip-path)** — photos "unveil" bottom-up instead of plain fade. CSS: `.curtain img{clip-path:inset(0 0 100% 0);transition:clip-path 1.1s cubic-bezier(.19,1,.22,1)}` + `.curtain.in img{clip-path:inset(0 0 0 0)}`. **Piggyback the EXISTING reveal IO** — add `curtain` as a second class on the same element (`class="resto-img reveal curtain"`), zero new JS, it reuses the `.in` class the blur-reveal observer already toggles. Reduced-motion: `clip-path:none`.

10. **Sheen / shine sweep on CTA** — diagonal light glides across a button on hover. CSS: `.btn::after{content:'';position:absolute;top:0;left:-80%;width:50%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.35),transparent);transform:skewX(-20deg);pointer-events:none;transition:left .55s ease}` + `.btn:hover::after{left:130%}`. Requires `.btn{position:relative;overflow:hidden}`.

## Seamless marquee

```css
.marquee{overflow:hidden;border-top/bottom hairlines;padding:17px 0}
.mtrack{display:flex;width:max-content;animation:mscroll 30s linear infinite;will-change:transform}
@keyframes mscroll{to{transform:translateX(-50%)}}
```

Duplicate the track content once (`track.innerHTML += track.innerHTML`) so -50% lands exactly on the seam — no JS animation needed. Linear easing IS correct here (constant conveyor); the one linear exception.

## Scroll progress bar — piggyback Lenis rAF

Don't run a second rAF loop or scroll listener; update the bar inside the same rAF that drives Lenis:

```js
function raf(time){
  if (lenis) lenis.raf(time);
  const max = document.documentElement.scrollHeight - innerHeight;
  progressBar.style.width = (max > 0 ? scrollY / max * 100 : 0) + '%';
  requestAnimationFrame(raf);
}
requestAnimationFrame(raf);
```

Works even when lenis is null (reduced-motion/offline fallback) since the loop runs unconditionally.

## Pitfalls (all hit in production)

- **Custom lerp smooth-scroll (window.scrollTo per rAF) breaks IO reveals** — constant scroll events starve IntersectionObserver; reveals stuck (3/11 fired). Native `scroll-behavior:smooth` or Lenis instead. Lenis is safe with IO because it uses native scroll + rAF smoothing.
- **`HTMLCollection.children.forEach` is not a function** — `.children` is HTMLCollection (no forEach); use `Array.from(el.children).forEach`. One occurrence kills everything after it in the handler (e.g. GSAP slide animates but counter/dots never update — exception before `current = i`).
- **Flexbox + translateX slider = blank slides** — slides in a flex row with `translateX(off*100%)` compute offsets from their flex position, so off-screen slides land wrong (active slide at left:1168 while slider is at 97). Symptom: "only slide 1 shows, 2&3 blank". Fix: absolute-positioned slides.
- **`loading="lazy"` on slider imgs** — off-viewport slides never load until scrolled; active slide shows blank. All slider imgs need `loading="eager" decoding="async"`.
- **Auto-advance timer confuses debugging** — a 5s interval makes manual click tests look broken (slide already advanced). Reset timer on interaction (`resetTimer()` inside `go()`).
- **Parallax floating element must fit the scene** — a big product photo over a hero as scroll-parallax reads as broken ("why is the gulai following me down?"). Pier88's plate works because it's part of the photographed scene. Keep parallax to bg layers, or make the float small + scene-integrated (gradient fade, low opacity).
- **Reduced-motion reset must cover everything** — reveal blur (`filter:none`), split-line (`transform:none`), Ken Burns (`animation:none`), parallax wrappers (`transform:none!important`). Missing one = element stuck hidden/blurred for motion-sick users.
- **Injecting a JS block by replacing `</script>` grabs the WRONG tag** — the first `</script>` in the file is usually the `<script src="...lenis...">` tag, and a `<script src>` element's body is IGNORED by the browser (its content never runs). Replacing the first `</script>` inserts your block where it silently never executes (symptom: side-effect missing, `node --check` still passes, console still empty). Anchor the insert on the main inline script's first distinctive content line (e.g. `// ---------- Lenis smooth scroll ----------`) or insert before the FINAL `</script>`, never a blanket `.replace('</script>', ...)`.
- **Inline-JS edits keep mangling empty parens** — writing JS through patch/execute_code can repeatedly drop `` so `apply;` lands as `apply;`, `(function {` as `(function {`. Write a small fixer `.py` to /tmp via `write_file`, build blank parens as `chr(40)+chr(41)`, run it, then re-verify with `node --check` AND a side-effect probe (dot count, computed transform, `style.display`). A proc that ends up `defined-but-not-invoked` (see IIFE pitfall) is still valid syntax, so `node --check` alone is blind to it.
- **IIFE defined-but-not-invoked is a SILENT bug** — if an IIFE's closing invoke-parens get dropped (written `});` instead of `});`), the function is *defined* but never *called*. It is still perfectly valid JS, so `node --check` passes and the browser console shows 0 errors. Symptom: the widget's init side-effects never happen — slider slides stay `position:absolute` stacked all opacity=1 (overlapping), dots array empty (`.sdot` count 0), counter frozen at its hardcoded initial, `style.display` never set to `block`. Other IIFEs that closed correctly keep working, so you see `reveal.in`/`split-line.in` populated but the slider dead. Diagnose by checking for the expected *side-effect* (dot count, computed transform, `style.display`) rather than waiting for a console error — there won't be one.

## Verification

1. `node --check` extracted `<script>` (python regex `<script type="module">(.*?)</script>` → /tmp, then node --check).
2. Browser: 0 JS errors; fresh-error probe (arm `window.addEventListener('error')` AFTER reload — buffered old errors from before a fix pollute console reads).
3. Slider: check each slide lands at slider's left edge (`getBoundingClientRect().left` ≈ slider left) when active — catches the flex bug.
4. Parallax: scroll 400px, assert bg wrapper translateY changes AND plate/element translateY changes in opposite direction.
5. Reduced-motion emulation: all elements visible, no transform/filter/animation stuck.
6. **Side-effect probe (catches the defined-not-invoked IIFE)**: `node --check` and console-error checks BOTH miss it, so assert the widget's init actually ran — `.sdot`/dot count > 0, `#menuSlider` has an inline `display:block`, only one slide has `opacity:1` with the rest `0`, counter text != its hardcoded initial value. If reveals fire but one widget is dead, suspect a malformed IIFE closing (`});` vs `});`) on that specific block.
