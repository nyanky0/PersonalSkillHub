---
name: invitation-web-pattern
description: Use when building undangan-style landing or portfolio pages.
---

# Invitation-Style Web Pattern (undangan → portfolio)

Indonesian digital-invitation UX ("undangan digital") applied to landing/portfolio pages. User request pattern: "bikin seperti undangan website". Class-level pattern; subject matter varies (wedding, portfolio, product launch).

## Signature undangan anatomy

1. **Cover/gate** — full-screen overlay hiding content: monogram/names, date or tagline, one "Open" button.
2. **Guest personalization** — name injected via query param (`?to=Nama`) into greeting text.
3. **Ceremony opening** — click triggers staged reveal: envelope flap rotates (rotateX), card slides up, then overlay parts/fades. Doors-part variant: two halves translateX outward.
4. **Music toggle** — floating button, autostarts AFTER the open click (gesture unlocks audio), persists preference.
5. **Scroll narrative** — one-page vertical scroll, sections framed as "events": intro → details → gallery → RSVP/contact → closing thanks.
6. **Closing** — gratitude section + share button (WhatsApp deep link common in Indonesia).

## Mapping to portfolio (non-wedding subject)

| Undangan element | Portfolio equivalent |
|---|---|
| Couple names + photo | Owner name + portrait |
| Event details | Experience/timeline |
| Gallery | Projects/work |
| RSVP button | Contact/Hire CTA |
| Countdown | Optional: availability date |
| Gift info | Skip unless relevant |

## Implementation rules

- Single-file HTML/CSS/JS preferred (user convention); no build step.
- Gate overlay: `position:fixed inset:0`, body scroll locked until opened (`overflow:hidden` on html/body, release on open).
- Reveal animation: transform/opacity/clip-path only; stagger children; ~0.8–1.2s total; `cubic-bezier(0.22,1,0.36,1)` feel.
- Revisit skip: `sessionStorage.getItem('opened')` → auto-open instantly, still render gate briefly for flash-of-content prevention.
- Audio unlock MUST happen inside the click handler (browser autoplay policy); toggle icon swap; loop on.
- Honor `prefers-reduced-motion`: skip ceremony, instant open.
- iOS Safari: use `100dvh` not `100vh` for gate height.

## Pitfalls

1. Autoplaying music before any user gesture = silently blocked; tie start to Open click.
2. Heavy Lottie/GIF on gate = slow first paint on Indonesian mobile networks; CSS transforms suffice.
3. Forgetting scroll-lock → users see content behind translucent gate.
4. Guest-name param must be URL-decoded and escaped before injection (XSS at trust boundary).
5. Don't reuse the same visual DNA across redesigns of the same site — user rejects near-clones; rebuild identity per version.

## Verification checklist

- [ ] Content unreachable (scroll + keyboard) until Open clicked
- [ ] Music starts only after gesture; toggle works
- [ ] Direct visit with `?to=` renders personalized name
- [ ] Reduced-motion path opens instantly
- [ ] No horizontal overflow during door/flap transforms
- [ ] Works offline-ish: no blocking external deps

Research notes and source links: see `references/research-notes.md`.