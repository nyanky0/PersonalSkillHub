# Research notes — undangan pattern + premium front-end signals

Collected 2026-08 session while researching "portfolio as digital invitation" redesign.

## Undangan digital (Indonesian market) feature set
Source: wevitation.com, invitly.id, undangannikah.id, galeriimaji.com, garapundangan.com marketing pages.

Standard paid-tier features:
- Envelope/cover opening animation (the core differentiator; "buka amplop")
- Background music with toggle
- Guest name personalization via link param (`?to=`), sometimes QR-coded guest list
- Countdown timer to event date
- Gallery (photo/video), love-story timeline
- RSVP form online
- Digital gift / kado cash links
- Event planner / maps integration
- AI-assisted copywriting on some platforms

UX consequence for builds: the gate+ceremony IS the product feel. Users judge by first 3 seconds of the open animation.

## Envelope animation technique (CodePen/logicalpython references)
- Flap: element with `transform-origin: top`, `rotateX(180deg)` on open, z-index swap mid-animation so card can slide above it.
- Card: translateY from inside envelope up past its edge, then scale/fade into full page.
- Pure CSS keyframes triggered by class toggle from one JS click handler.

## Awwwards-grade portfolio signals (muz.li, hontran.dev, wavespace roundups 2025-2026)
- Type-in-motion: letters stretch/snap/recombine on scroll, timeline-driven, must never block reading.
- Editorial modules: retro typographic touch, generous negative space, curatorial storytelling blocks.
- Motion + texture over flat cards: grain, paper, dynamic transitions.
- Signature interactions that read as craft: magnetic buttons, custom cursor follower, text mask reveals, hover image previews following cursor.

## Skills.sh ecosystem notes (for future skill sourcing)
- skills.sh indexes community agent skills; browsable at /skills, topics include React, Next.js, Design & UI, Testing.
- mattpocock/skills = high-signal family (tdd, diagnosing-bugs, codebase-design, grill-me, improve-codebase-architecture).
- vercel-labs/agent-skills/web-design-guidelines duplicates antfu-web-design-guidelines content.
- Install path used successfully: `yes | hermes skills install skills-sh/<org>/<repo>/<skill>` (pipe yes required or install cancels).
