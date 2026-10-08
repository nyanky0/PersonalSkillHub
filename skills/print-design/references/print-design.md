# Print Design: HTML → PDF via Headless Chrome

Full technique guide for the `print-design` skill.

## Rendering Command

```bash
google-chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=output.pdf file:///path/to/input.html
```

Key flags:
- `--no-pdf-header-footer` — strips browser date/URL/title from print margins. Without this, PDF has "9/5/26, 10:39 AM" top-left and title top-right.
- `--no-sandbox` — required in WSL/Linux containers.
- `--disable-gpu` — avoids GPU init errors in headless.
- `file://` URL — must be absolute path. Use `file:///home/...` (three slashes).

## Verify Output

```bash
pdfinfo output.pdf   # page count, page size, encryption status
file output.pdf       # confirm valid PDF
```

For visual verification:
```bash
# Convert PDF page to image for inspection
pdftoppm -jpeg -r 150 output.pdf preview
```

## Print CSS Essentials

```css
@page {
  size: A4;       /* or 'letter', or custom like 420px 600px */
  margin: 0;       /* CSS controls all margins, not the printer */
}
```

- Set `@page` margin: 0 so the HTML layout controls all spacing.
- Fit content to one page: test with `pdfinfo` — if Pages > 1, reduce padding/font-size.
- Web fonts via `@import url('https://fonts.googleapis.com/...')` work in headless Chrome.
- `box-shadow` renders in PDF but may look different on print. Prefer borders.
- `clip-path` works but test — complex shapes can render unpredictably in print.
- `background: linear-gradient(...)` renders correctly in headless Chrome PDF.

## Copy to Windows Desktop (WSL)

```bash
cp /home/maulana/output.pdf /mnt/c/Users/<username>/Desktop/Name.pdf
```

Windows username discoverable at `/mnt/c/Users/`. Current user: `muham`.

## Anti-Slop Rules for Print Menus (User-Validated)

User explicitly rejected these as "AI slop" on a restaurant menu:

### REJECTED (AI slop tells in print design)
- **Gradient headers** (green→brown, blue→violet) — looks like a web template, not a printed menu
- **CSS clip-path mountain silhouettes** — over-engineered decoration that adds nothing
- **Radial gradient "sun" accents** — fake decorative elements
- **Glassmorphism, blurred overlays** — web-native effects that don't belong on paper
- **Generic serif fonts (Playfair Display)** for everything — feels templated
- **Decorative shadow box-shadows** — unnecessary for print
- **Rainbow or tech-gradient color palettes**
- **Centered hero + 3-card grid** — wrong surface for a menu (this is a Decide/Learn surface, not a menu)

### ACCEPTED (what the user liked)
- **Handwritten/cursive fonts** (Pacifico, Caveat) for headers — feels human, not generated
- **Warm cream paper background** (`#fdf6e9`, `#f4ecd8`) — evokes real printed paper
- **Warm earth palette**: brown (`#6b4423`), green (`#2d6a3e`), gold (`#d4a017`) — natural, appetizing
- **Simple double-border frames** with corner accents — traditional, not gradient boxes
- **Dotted leader lines** between item name and price — classic menu convention
- **Italic sub-items** (½ porsi) indented — clear hierarchy without decoration
- **Red accents for prices of main items** — draws eye, appetizing
- **Badge labels** ("BEST") on signature items — simple, effective attention grab
- **Section dividers** with simple lines + small ornament dot — not gradient bars
- **Footer with business info** (Cuci Motor · Cuci Mobil · Gogor) — contextual, not generic

## Iterative Workflow

1. Write HTML with print CSS (`@page`, embedded `<style>`)
2. Render: `google-chrome --headless ... --print-to-pdf`
3. Check: `pdfinfo` for page count (should be 1 for single-page menus)
4. If multi-page: reduce padding, font sizes, or spacing; re-render
5. Copy to Desktop if WSL: `cp out.pdf /mnt/c/Users/<user>/Desktop/`
6. User reviews and requests changes (text edits, design tweaks)
7. Patch HTML, re-render PDF, re-copy — fast iteration loop (seconds per cycle)

## Pitfalls

- `--print-to-pdf-no-header` is the old flag name. Use `--no-pdf-header-footer` (current).
- DBus errors (`org.freedesktop.UPower`) are harmless in WSL — Chrome still renders the PDF.
- `browser_vision` may fail on PDF viewer (blank canvas). Use `pdfinfo` + `file` to verify the PDF itself, not the browser viewer.
- Vision model 502 errors on kimi-k3 don't affect the PDF — screenshot is still saved to cache path for sharing.
- `google-chrome` must be installed: `sudo apt install google-chrome-stable` or equivalent.
- `pdfinfo` requires poppler-utils: `sudo apt install poppler-utils`.
