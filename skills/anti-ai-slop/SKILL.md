---
name: anti-ai-slop
description: "Unified Anti-Slop Master Engine (Prose, Copywriting, UI/Visual, Code Comments, WCAG Human Accessibility, & Mobile Reflow). Synthesizes anti-ai-slop, anti-ai-slop-writing, and github.com/miqdadbadjuber/anti-slop (antislop, antislop-copywriting, antislop-ui, antislop-code, antislop-human, antislop-layoutmobile)."
version: 3.0.0
author: Hermes Agent, Senpai & Miqdad Badjuber (anti-slop)
metadata:
  hermes:
    tags: [writing, prose, anti-slop, humanizer, ui, code-comments, accessibility, mobile-layout]
    related_skills: [anti-ai-slop-writing, antislop, antislop-copywriting, antislop-ui, antislop-code, antislop-human, antislop-layoutmobile, ai-agent-brain]
---

# Unified Anti-AI-Slop Master Engine v3.0

> **Symbiosis & Sub-Skills**:
> This master skill unifies the user's `anti-ai-slop` / `anti-ai-slop-writing` directives with the complete [`github.com/miqdadbadjuber/anti-slop`](https://github.com/miqdadbadjuber/anti-slop) suite:
> - **Prose & Copywriting**: [`anti-ai-slop-writing`](../anti-ai-slop-writing/SKILL.md) + [`antislop-copywriting`](../antislop-copywriting/SKILL.md)
> - **Core Mechanism & Delivery Gate**: [`antislop`](../antislop/SKILL.md)
> - **UI & Visual Restraint**: [`antislop-ui`](../antislop-ui/SKILL.md)
> - **Code Comment Hygiene**: [`antislop-code`](../antislop-code/SKILL.md)
> - **Human & WCAG Accessibility**: [`antislop-human`](../antislop-human/SKILL.md) (`contrast-check.py`)
> - **Mobile Layout Reflow**: [`antislop-layoutmobile`](../antislop-layoutmobile/SKILL.md)

---

## 1. The Core Mechanism: The Purpose Test (`antislop`)

Every design, copy, or code comment choice must pass **The Purpose Test**:
> **Why is this here, and what breaks or becomes less clear for the user if we remove it?**
- A valid reason is **specific to THIS product, module, or user task** (never "looks modern", "adds visual interest", or "standard template").
- **Operating Mode**: `during` (`%APPDATA%\antislop\settings.json` = `{"mode": "during"}`) — apply all rules silently while drafting/coding, and run the Delivery Gate silently before finishing.

### Three-Tier Rule Taxonomy
1. **FORBIDDEN AS DEFAULT (Allowed with Purpose)**:
   - Gradients, glassmorphism (max 1–2 elements), pill border-radius everywhere, large soft shadows, glow effects, background dot/line grids, stock photos, generic 3-step/bento/pricing templates, decorative status dots, monospace headings, decorative arrows on every CTA.
2. **HARD BANS (Zero Exceptions)**:
   - Fabricated metrics, fake testimonials, unverified "Trusted By" logos, `outline: none` without a `:focus-visible` replacement (3:1 contrast), empty links (`href="#"`), dead buttons, `lorem ipsum` or placeholder copy, decorative code-comment banners (`// =======`), restating-the-obvious comments.
3. **REQUIRED (Always)**:
   - Real specific copy, WCAG AA contrast (4.5:1 normal text, 3:1 large text & UI boundaries), keyboard navigation (`Tab`, `Enter`, `Space`, `Escape`), complete data states (Empty, Loading, Error — never color-only), and genuine mobile reflow (44x44px tap targets, zero horizontal scroll leak).

---

## 2. Prose & Copywriting Rules (7 Core Heuristics + `antislop-copywriting`)

1. **Kill filler & AI vocabulary** — Ban *seamless, unleash, empower, elevate, revolutionize, delve, tapestry, game-changer, cutting-edge, next-gen, robust, synergy, streamline, world-class, supercharge, unlock*. Consult [`references/phrases-en.md`](references/phrases-en.md) and [`../anti-ai-slop-writing/references/banned-words.md`](../anti-ai-slop-writing/references/banned-words.md).
2. **Break formulaic structures** — No Rule of Three defaults, no parataxis chains ("Short sentence. Then another. Then another."), no binary contrasts ("Not X, but Y"), no hedging seesaws, no eyebrow pills duplicating the H1.
3. **Enforce active voice & concrete nouns** — Name the exact table (`inventory_transfers`), service (`SapB1Service`), or human operator. Replace vague claims with real numbers and workflows.
4. **Vary sentence cadence** — Mix 4-word sentences with 28-word subordinate clauses. Never write three consecutive sentences of uniform length.
5. **Strict punctuation hygiene** — Max 1 em dash per 500 words; max 1 exclamation mark per 1,000 words; zero decorative emoji in UI headers, tables, or code comments.
6. **Action-specific CTAs** — Button labels state the exact outcome ("Simpan Seri", "Buat Inventory Transfer", "Tarik Item PL OUT"), never generic "Get Started", "Learn More", or "Submit".
7. **Indonesian Anti-Slop** — Gunakan kalimat aktif lugas. Hilangkan pembuka klise (*"perlu diketahui bahwa"*, *"tidak dapat dipungkiri"*, *"hadir sebagai solusi"*). Sebutkan nama modul, tabel, atau dokumen secara presisi.

---

## 3. Code Comment Hygiene (`antislop-code`)

- **Delete**: Decorative separators (`// ================`), step-by-step workflow narration (`// Step 1: Validate`), signature echoes, empty labels (`// Main logic`), vague TODOs (`// TODO: improve`), and closing brace markers (`} // end if`).
- **Keep (1–2 lines max)**: Non-obvious business rules, SAP B1 Service Layer / DI API traps, concurrency locks, security invariants, and protocol constraints. Explain *why*, never *what*.

---

## 4. UI, Human Accessibility & Mobile Reflow (`antislop-ui` + `antislop-human` + `antislop-layoutmobile`)

- **Palette & Surface Restraint**: 2–3 core colors + 1 deliberate accent (`ibt-600`). Solid white/slate surfaces (`bg-white border-slate-200`); no unmotivated dark-mode or neon glows.
- **WCAG AA Contrast**: Verify grey pairings mathematically (never eyeball `#777777` on `#FFFFFF` which fails at 4.48:1; use `slate-600` / `slate-700` on white).
- **States & Keyboard**: Every table/view must have explicit Empty, Loading, and Error states with text + icon (never color alone). Every modal closes on `Escape`.
- **Responsive Reflow**: Multi-column grids stack cleanly across phone, tablet, and desktop; tables use `overflow-x-auto` containers so the page never leaks horizontal scroll; touch targets >= 44x44px.
