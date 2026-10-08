---
name: vercel-webdesign
description: "| Vercel / Geist-inspired premium web design language."
---

# Vercel Web Design Language

A refined, technical, high-craft aesthetic. Vercel's design = extreme clarity,
subtle depth, monochrome-forward surfaces with one or two accents, sharp
typography, and micro-interactions that feel engineered.

## 1. Typography

- **Primary:** Geist Sans (Vercel's typeface) — `@fontsource/geist-sans` or
  Geist from `vercel.com/font`. Fallback: Inter.
- **Code/mono:** Geist Mono or JetBrains Mono for code blocks, labels, badges.
- **Scale:** Big, confident hero headlines (clamp: `clamp(2.5rem, 6vw, 4.5rem)`,
  tight letter-spacing `-0.02em to -0.04em`). Body at 16-18px, `line-height 1.6`.
- **Weight contrast:** Use only 400/500/600. Never font-weight 300 on dark.
- Paragraph max-width ~65ch.

## 2. Color

- **Surfaces:** Near-black `#000` / `#0A0A0A`, white `#fff`, and neutral grays
  via `neutral` scale (Tailwind `neutral-900/800/…`).
- **Borders:** `white/10` (dark) or `black/10` (light) — hairline 1px borders.
  Borders create structure more than shadows.
- **Accent:** ONE accent color — Vercel uses black-on-white or white-on-black
  with a single accent like `#0070F3` (blue) sparingly. Avoid rainbow UIs.
- **Text hierarchy:** 3 levels max: primary (near-white/near-black), secondary
  (`white/60` or `neutral-500`), tertiary/muted (`white/40`).
- Dark mode is the default "wow" look for dev tools; light must also be clean.

## 3. Layout & Spacing

- **Generous, consistent spacing:** 8px grid; sections at `py-24 md:py-32`.
- **Centered max-width containers:** `max-w-7xl mx-auto px-6 lg:px-8`.
- **Grid/table systems:** Precise, aligned columns for pricing, features, logos.
- **Asymmetric but balanced:** hero often left-aligned text + right-side visual
  (terminal window, product screenshot, code).

## 4. Components & Patterns

- **Navbar:** Fixed, frosted `backdrop-blur`, hairline bottom border, centered
  max-width, logo left, links center (subtle), CTA right (small button/sign-in).
- **Hero:** One idea. Headline + subheadline (secondary color) + primary & ghost
  CTAs + a product visual below. Add subtle "spotlight" radial gradient behind.
- **Terminal windows:** Rounded `rounded-lg` with top bar dots, dark `#0A0A0A`,
  mono text — great for showing code/CLI in heroes.
- **Cards:** `rounded-lg/xl`, hairline border, `hover:border-white/20`,
  `hover:bg-white/[0.02]`, smooth `transition`. Optional subtle glow on hover.
- **Badges:** Small pill `text-[13px]` with dot, e.g. "✦ New: Edge Functions".
- **Logo cloud:** Grayscale logos, `grayscale opacity-60` → full on hover.
- **Feature grid:** 2-4 col bento-ish asymmetric grids; icons in bordered tiles.
- **Footer:** Dense, multi-column links in muted color, hairline top border.

## 5. Motion & Interaction (restrained, engineered)

- Micro-interactions only: `transition-all duration-200/300`, hover lifts at
  most `-translate-y-0.5`, opacity/border-color changes.
- Subtle entrance animations (fade-up with stagger), no garish bounce.
- Respect `prefers-reduced-motion`.
- Buttons: rounded-full or rounded-lg, small but not tiny, clear hover state,
  `active:scale-[0.98]` pressed feedback.

## 6. Do / Don't

- DO: monochrome-first, hairline borders, one accent, tight prose, real product
  mockups/terminals, consistent 8px rhythm, generous whitespace.
- DON'T: purple-blue gradients everywhere, glowing neon spam, random shadows,
  crowded multi-gradients, bone-stock Tailwind defaults with chunky borders,
  "clever" 3D tilt on everything, default browser look.

## 7. Stack Notes

Best with Tailwind CSS (`tailwind.config` extended with Geist fonts), Next.js/React
or preact, and Vercel deployment. If the project uses plain HTML/CSS, replicate
the same tokens via CSS custom properties under `:root` / `[data-theme=dark]`.

## Quick Reference — Tailwind token recipe

```js
// tailwind.config.js
theme: {
  extend: {
    fontFamily: {
      sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
      mono: ['Geist Mono', 'ui-monospace', 'monospace'],
    },
    colors: {
      surface: { DEFAULT: '#0A0A0A', dark: '#000', light: '#fff' },
      accent: { DEFAULT: '#0070F3' },
    },
  },
}
```

Deliver: clean, engineering-grade, editorially refined interfaces. If the user
says "just use Vercel style" — hero + features + pricing + logos + CTA + footer,
all matching the above.
