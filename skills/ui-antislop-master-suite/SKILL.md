---
name: ui-antislop-master-suite
description: "Master Unified Anti-Slop UI & Design Engineering Suite. Consolidates anti-slop rules, exact Tailwind tokens, human accessibility, mobile reflow, and enterprise aesthetic patterns."
version: 1.0.0
author: Hermes Agent (Miku) & Senpai
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ui, frontend, antislop, design, tailwind, accessibility, styling]
    related_skills: [antislop-ui, anti-ai-slop, ui-styling, antislop-human, antislop-layoutmobile, ui-design-themes, popular-web-designs]
---

# UI Anti-Slop Master Suite

Master standard untuk rekayasa UI frontend berkualitas enterprise tanpa template AI generik (*zero-slop*), ramah aksesibilitas manusia, dan tata letak responsif adaptif.

---

## 1. Zero-AI-Slop Visual Rules (Core Invariant)

### Pantangan Mutlak (Forbidden Tells):
1. **Generic Blue-Purple Gradient / Glow**:
   - Dilarang memakai gradien biru-ke-ungu/cyan atau radial glow acak di belakang hero tanpa identitas brand.
   - *Fix*: Ambil palet dari brand identity / `DESIGN.md`. Gradien hanya boleh dipakai sebagai pemisah hierarki terukur.
2. **Excessive Glassmorphism**:
   - Dilarang memberi blur/backdrop-filter di navbar, card, modal, dan sidebar sekaligus.
   - *Fix*: Maksimal 1-2 elemen dengan glassmorphism (biasanya navbar sticky atau active overlay). Elemen lain harus solid.
3. **Pill-Shape Monoculture**:
   - Dilarang membuat semua tombol, input, card, badge, dan modal berbentuk kapsul (*full rounded pill*).
   - *Fix*: Gunakan skala radius konsisten (e.g. `rounded-lg` untuk card/input, `rounded-md` untuk button).
4. **Floating Marketing Badges & Sparkles**:
   - Dilarang menambahkan badge "✨ Powered by AI" atau icon glitter mengambang tanpa fungsi teknis.

---

## 2. Component Implementation & Token Architecture

- **Komponen Fungsional**: Bangun komponen menggunakan basis shadcn/ui, Radix primitives, atau Vue/React headless pattern.
- **Tailwind Utility Standards**: Gunakan semantic classes (e.g. `bg-card`, `text-foreground`, `border-border`) agar support tema dark/light mode secara native.
- **Zero Hallucination UI**: Komponen form dan tabel wajib berparitas 1:1 dengan skema database dan API kontrak riil.

---

## 3. Human Accessibility & Mobile Reflow

- **WCAG Contrast Check**: Kontras teks dengan background minimal 4.5:1 untuk normal text dan 3:1 untuk large text.
- **Touch Target**: Minimal target sentuh pada layar mobile adalah 44x44px.
- **Reflow & Layout**:
  - Hindari horizontal overflow (`overflow-x: hidden` liar yang menelan konten).
  - Gunakan Flexbox/CSS Grid yang membungkus rapi (*wrap*) saat viewport mengecil.

---

## 4. Curated Enterprise Aesthetics

Gunakan gaya visual profesional yang terbukti di dunia nyata (Linear, Vercel, Stripe style):
- Tipografi tajam dengan hierarki font-size dan font-weight jelas (`text-sm font-medium`, `text-2xl font-semibold`).
- Border tipis terukur (`border border-neutral-200 dark:border-neutral-800`).
- Subtle micro-interactions (hover transisi 150ms-200ms `ease-out`).
