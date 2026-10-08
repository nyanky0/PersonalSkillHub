---
name: print-design
description: "HTML to PDF print artifacts. Use for menus and flyers."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [print, pdf, html, design, menu, flyer, anti-slop, chrome, headless]
    related_skills: [claude-design, pdf, sketch]
---

# Print Design: HTML → PDF via Headless Chrome

Use this skill when the user wants a **printable artifact** — restaurant menu, price list, flyer, poster, brochure, info sheet — designed as HTML/CSS then rendered to PDF via headless Chrome. This gives full CSS control (fonts, dotted leaders, layout) that reportlab/pypdf cannot match.

**Trigger phrases:** "buatkan daftar harga", "menu untuk print", "cetak PDF", "print flyer", "rancang menu", "pdf untuk di-print", "buat PDF bagus".

**NOT for:** editing existing PDFs (use `nano-pdf` or `pdf` skill), multi-page documents/reports (use `pdf`/`docx`), or web page design (use `claude-design`).

See [references/print-design.md](references/print-design.md) for the full technique guide — rendering commands, print CSS essentials, copy-to-Desktop (WSL), anti-slop rules, and iterative workflow.

See [templates/menu-template.html](templates/menu-template.html) for a starter restaurant menu template — copy and modify.

## Quick Start

```bash
# 1. Write HTML with print CSS
# 2. Render to PDF
google-chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=output.pdf file:///absolute/path/to/input.html

# 3. Verify
pdfinfo output.pdf   # check page count (should be 1 for single-page menus)
file output.pdf       # confirm valid PDF

# 4. Copy to Windows Desktop (WSL)
cp output.pdf /mnt/c/Users/<username>/Desktop/Name.pdf
```

## Key Rules

1. **`@page { size: A4; margin: 0; }`** — CSS controls all margins.
2. **`--no-pdf-header-footer`** — strips browser date/URL/title from print.
3. **Fit to one page** — check `pdfinfo`. If Pages > 1, reduce padding/font-size.
4. **Web fonts via `@import`** work in headless Chrome. No need to self-host.
5. **Iterate fast** — patch HTML → re-render → re-copy. Seconds per cycle.

## Anti-Slop Rules (User-Validated)

User explicitly called out "AI slop" on print design. These are the DO/DON'T for print menus:

### DON'T (AI slop tells in print)
- Gradient headers (green→brown, blue→violet) — web template look
- CSS clip-path decorative shapes (mountain silhouettes, suns) — over-engineered
- Glassmorphism, blurred overlays — web-native, not for paper
- Generic serif (Playfair Display) for everything — templated
- Decorative box-shadows — unnecessary for print
- Rainbow/tech-gradient palettes
- Centered hero + 3-card layout — wrong surface for a menu

### DO (what works)
- Handwritten/cursive fonts (Pacifico, Caveat) for headers — human feel
- Warm cream paper background (#fdf6e9, #f4ecd8) — real paper vibe
- Earth palette: brown (#6b4423), green (#2d6a3e), gold (#d4a017) — appetizing
- Simple double-border frames with corner accents — traditional
- Dotted leader lines between item name and price — classic menu convention
- Italic indented sub-items (½ porsi) — clear hierarchy
- Red accents for main item prices — draws eye
- Badge labels ("BEST") on signature items — simple attention grab
- Section dividers: simple lines + small ornament dot
- Footer with business info — contextual, not generic

## Pitfalls

- `--print-to-pdf-no-header` is the OLD flag. Use `--no-pdf-header-footer`.
- DBus errors (`org.freedesktop.UPower`) harmless in WSL — Chrome still renders.
- `browser_vision` may blank on PDF viewer. Use `pdfinfo` + `file` to verify the PDF.
- Vision model 502s don't affect PDF — screenshot still saved to cache for sharing.
- User dislikes verbose design. Iterate on user feedback, don't explain each pixel.

## Workflow

1. Write self-contained HTML (`<style>` embedded, `@page` set)
2. Render: `google-chrome --headless ... --print-to-pdf`
3. Check `pdfinfo` for page count
4. If multi-page: reduce padding/fonts, re-render
5. Copy to Desktop if WSL
6. User reviews → patch HTML → re-render → re-copy (fast loop)
7. Save final HTML as template for future use

## Related Skills

- `claude-design` — design process/taste for web artifacts (bundled, read-only)
- `pdf` — PDF manipulation (merge, split, extract, forms)
- `nano-pdf` — natural-language text edits in existing PDFs
- `sketch` — HTML mockup variants for comparison
