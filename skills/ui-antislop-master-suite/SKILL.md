---
name: ui-antislop-master-suite
description: "Anti-AI-slop UI design suite: strict Tailwind tokens, human accessibility, and mobile reflow."
version: 1.1.0
author: Hermes Agent (Miku) & Senpai
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ui, frontend, antislop, design, tailwind, accessibility, styling, micro-interactions, craft]
    related_skills: [antislop-ui, anti-ai-slop, ui-styling, make-interfaces-feel-better, antislop-human, antislop-layoutmobile, ui-design-themes, popular-web-designs, simple-english, appllama-app-design-skill]
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

---

## 5. Micro-Craft & Interface Feel (Jakub Krehel Standard)

Aturan presisi tingkat mikro untuk memastikan interface terasa responsif, taktil, dan organik:

1. **Concentric Border Radius**:
   - Untuk nesting kontainer rounded yang berdekatan: `R_outer = R_inner + padding`.
   - Menghindari sudut lancip atau padding aneh di dalam card/button bertingkat.
2. **Optical vs Geometric Alignment**:
   - Penjajaran geometris murni seringkali terlihat miring secara optik (misal icon panah, play triangle `▶`, star).
   - Selalu berikan offset micro-padding/margin (1-2px) agar seimbang secara visual di mata manusia.
3. **Typography & Tabular Numbers**:
   - `text-wrap: balance` wajib untuk heading / title pendek (mencegah orphan words).
   - `text-wrap: pretty` untuk paragraf deskripsi singkat & caption.
   - `font-variant-numeric: tabular-nums` (Tailwind: `tabular-nums`) wajib untuk semua angka yang berubah dinamis (harga, counter, tabel finansial) agar tidak loncat saat update.
4. **Subtle Image & Surface Outlines**:
   - Berikan outline tipis 1px inset pada gambar/avatar agar tidak menyatu dengan background:
     `outline: 1px solid rgba(0, 0, 0, 0.08); outline-offset: -1px;` (di dark mode gunakan `rgba(255, 255, 255, 0.1)`).
5. **Tactile Press Feedback & Hit Targets**:
   - Minimal area sentuh mobile `44x44px` (desktop minimal `40x40px`).
   - Berikan feedback taktil halus pada `:active`: `transform: scale(0.97)` dengan transisi cepat 100ms.
   - Animasi wajib *interruptible* (jangan pernah mengunci interaksi pengguna saat animasi berjalan).



---

## 6. Controlled Technical Prose & Documentation (ASD-STE100 / Simple English)

Selain antislop visual dan copywriting UI, prosa teknis dan dokumentasi sistem wajib mematuhi standar **ASD-STE100 Issue 9** melalui skill `simple-english`:
- **Instruksi Prosedural**: Maksimal 20 kata per kalimat, kalimat imperatif, 1 instruksi per kalimat.
- **Kondisi Sebelum Perintah**: Format *"Jika [kondisi], lakukan [perintah]"* (contoh: *"If the sync fails, check the log."*).
- **Eliminasi Kata Hampa AI**: Hapus kata-kata tanpa fakta seperti *"seamlessly"*, *"robust"*, *"crucial"*, *"leverage"*, dan *"not just X, but Y"*.
- **Register Baku**: Rujuk `references/rule-catalog.md` dan `references/word-swaps.md` di skill `simple-english`.


---

## 7. Native Mobile Anti-Slop & Build Bar (Appllama Standard)

Untuk antarmuka aplikasi mobile (React Native / Expo / Capacitor / Mobile Web), patuhi standar rekayasa dari skill `appllama-app-design-skill`:
- **Apple HIG Fidelity & Semantic Tokens**: Wajib gunakan warna semantik platform asli (`systemBackground`, `label`, `separator`), bukan warna heksadesimal statis acak.
- **Navigasi Semantik & One-Way Doors**:
  - Gunakan `push` untuk hierarki detail bertingkat.
  - Gunakan `sheet / modal` untuk task mandiri (creation / editing).
  - Terapkan *one-way doors*: hilangkan tombol back pada alur krusial (misal layar sukses checkout, pasca-paywall, atau konfirmasi transaksi).
- **Off-JS Thread Motion Physics**: Semua animasi wajib berjalan di thread native (Reanimated spring physics dengan kecepatan jari nyata), dilarang mengunci thread JavaScript.
- **Simulator-Verified Loop**: Verifikasi visual wajib diuji langsung pada simulator mobile, mengaudit performa gesture dan transisi layar nyata (bukan sekadar resize browser desktop). Rujuk detail pada sub-panduan `references/motion.md` dan `references/native-controls.md`.
