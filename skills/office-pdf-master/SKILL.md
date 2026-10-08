---
name: office-pdf-master
description: "Master PDF reading, text editing in-place, merging, and OCR extraction via PyMuPDF and pdfplumber."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [pdf, ocr, pdf-editing]
---

# Office Pdf Master



## Sub-Module: pdf

# PDF Skill

Create PDFs from structured specs, build and fill AcroForm forms (with layout linting and visual overlays), extract text/tables/metadata, merge/split/rotate/watermark/stamp pages, export page images, manage metadata and attachments, and encrypt/decrypt — using pypdf, reportlab, and pdfplumber. Scanned (image-only) PDFs contain no text layer: OCR is explicitly out of scope here — when a page is image-only, stop and use the `ocr-and-documents` skill instead of pretending to extract text.

## When to Use

- Generate a report, invoice, or multi-page document as PDF.
- Build a fillable AcroForm (text/checkbox/radio/dropdown) from a JSON spec, linting the layout first.
- Pull text, tables (JSON/CSV), metadata, or form-field values out of a PDF.
- Merge, split, rotate, extract page subsets, watermark, stamp text/images at coordinates, bookmark, or compress PDFs.
- Export pages as PNGs for visual review or for OCR hand-off; set/clear document metadata; add/extract file attachments.
- Fill or flatten AcroForm forms; encrypt or decrypt with passwords.
- NOT for scanned/image-only PDFs (use `ocr-and-documents`) and NOT for pixel-perfect HTML-to-PDF rendering (use a headless browser).

## Prerequisites

- Python 3.10+ with `pypdf`, `reportlab`, `pdfplumber`:
  `python -m pip install pypdf reportlab pdfplumber`
- Optional, for page rasterization (`pdf_page_image.py`, overlay rendering): `python -m pip install pypdfium2`, or poppler's `pdftoppm` on PATH. Scripts fall back pypdfium2 → pdftoppm and report `{"rendered": false, "missing": [...]}` (exit 0) when neither exists.
- Each helper script checks imports lazily and prints an install hint if a dependency is missing.

## How to Run

All helpers live in `scripts/` and are argparse CLIs — run them with the `terminal` tool; every one supports `--help`. They read/write JSON strictly as UTF-8, print JSON results to stdout, and exit non-zero on failure.

```bash
python scripts/pdf_create.py spec.json -o out.pdf         # build PDF from JSON spec
python scripts/pdf_make_form.py formspec.json -o form.pdf # build fillable AcroForm from JSON spec
python scripts/pdf_form_layout.py formspec.json           # lint form layout BEFORE building
python scripts/pdf_form_layout.py formspec.json --render-overlay boxes.png [--pdf form.pdf]
python scripts/pdf_read.py doc.pdf --text                 # per-page text (JSON)
python scripts/pdf_read.py doc.pdf --tables --csv-dir t/  # tables to JSON + CSV files
python scripts/pdf_read.py doc.pdf --meta                 # metadata, page sizes, encrypted/scanned flags
python scripts/pdf_read.py form.pdf --fields              # form fields: name, type, value
python scripts/pdf_merge.py a.pdf b.pdf -o merged.pdf [--bookmarks]
python scripts/pdf_split.py doc.pdf --pages 1-3,7 -o part.pdf [--rotate 90]
python scripts/pdf_fill_form.py form.pdf --fields-json values.json -o filled.pdf [--flatten]
python scripts/pdf_secure.py doc.pdf --encrypt -o enc.pdf --user-password your-password
python scripts/pdf_secure.py enc.pdf --decrypt -o dec.pdf --password your-password
python scripts/pdf_watermark.py doc.pdf --stamp mark.pdf -o stamped.pdf [--under]
python scripts/pdf_stamp.py doc.pdf -o out.pdf --text "DRAFT" --x 150 --y 400 \
    --font-size 60 --rotation 45 --opacity 0.3 --color "#cc0000" [--pages 1-3]
python scripts/pdf_stamp.py doc.pdf -o out.pdf --image sig.png --x 400 --y 60 --width 120
python scripts/pdf_page_image.py doc.pdf --pages 1-3 --dpi 150 --out-dir imgs/
python scripts/pdf_meta.py doc.pdf --set-meta --title "T" --author "A" -o out.pdf
python scripts/pdf_meta.py doc.pdf --attach data.csv -o out.pdf
python scripts/pdf_meta.py doc.pdf --list-attachments | --extract-attachments dir/
```

## Quick Reference

| Task | Tool | Command / API |
|---|---|---|
| Create doc (headings, tables, images) | reportlab platypus | `pdf_create.py spec.json -o out.pdf` |
| Build fillable form | reportlab acroForm | `pdf_make_form.py formspec.json -o form.pdf` |
| Lint form layout / overlay image | pure python + PIL | `pdf_form_layout.py formspec.json [--render-overlay o.png]` |
| Per-page text | pdfplumber | `pdf_read.py f.pdf --text` |
| Tables → JSON/CSV | pdfplumber | `pdf_read.py f.pdf --tables` |
| Metadata / sizes / encrypted / scanned | pypdf + pdfplumber | `pdf_read.py f.pdf --meta` |
| Merge (+ outline) | pypdf | `pdf_merge.py a.pdf b.pdf -o m.pdf` |
| Split / extract / rotate | pypdf | `pdf_split.py f.pdf --pages 2-5 --rotate 90` |
| List / fill / flatten form | pypdf | `pdf_read.py --fields`, `pdf_fill_form.py` |
| Encrypt / decrypt (AES-256) | pypdf | `pdf_secure.py --encrypt/--decrypt` |
| Watermark / stamp PDF page | pypdf | `pdf_watermark.py f.pdf --stamp w.pdf` |
| Stamp text/image at coordinates | reportlab + pypdf | `pdf_stamp.py f.pdf --text "Sign here" --x 400 --y 60` |
| Pages → PNG (review / OCR hand-off) | pypdfium2 or pdftoppm | `pdf_page_image.py f.pdf --pages 1-3 --out-dir imgs/` |
| Set/clear metadata, attachments | pypdf | `pdf_meta.py --set-meta / --attach / --extract-attachments` |
| Compress content streams | pypdf | `pdf_split.py f.pdf --pages 1-N --compress` |

## Procedure

1. **Inspect first.** Run `pdf_read.py file.pdf --meta`. Check `encrypted` (if true, decrypt first with `pdf_secure.py --decrypt`) and `likely_scanned_pages`. If pages are image-only, export them with `pdf_page_image.py --pages <scanned> --dpi 300 --out-dir imgs/` and hand the PNGs to the `ocr-and-documents` skill — do not report empty text as "no content".
2. **Create.** Write a JSON spec with `write_file` (elements: `heading`, `paragraph`, `table`, `image`, `pagebreak`; optional `title`/`author` metadata; page numbers are added automatically), then run `pdf_create.py`. Verify visually with `vision_analyze` on a rendered page image if layout matters.
3. **Extract.** `--text` gives a JSON list of per-page strings; `--tables` gives row arrays per page and can also emit CSV files. Read results with `read_file`; never eyeball a binary PDF directly.
4. **Manipulate.** `pdf_merge.py` concatenates and can add one bookmark per source file; `pdf_split.py` handles page ranges (1-based, e.g. `1-3,5,9-`), rotation in 90° steps, and `--compress`. Watermark by preparing a single-page stamp PDF (e.g. via `pdf_create.py`) and overlaying it with `pdf_watermark.py`; for one-liner stamps ("sign here", diagonal DRAFT, corner labels) use `pdf_stamp.py` with text or an image at explicit coordinates.
5. **Build forms.** Write one form-spec JSON (fields with `label_box`/`entry_box` in PDF points — see `references/forms.md`), lint it with `pdf_form_layout.py` and fix every reported problem, optionally review the `--render-overlay` PNG with `vision_analyze`, then build with `pdf_make_form.py` and confirm with `pdf_read.py --fields`.
6. **Fill forms.** List fields (`--fields`) to learn exact names and types, write a UTF-8 JSON of `{"FieldName": "value"}` with `write_file` (checkboxes accept `true`/`false`; radio/choice values must match the field's export options), then `pdf_fill_form.py`. Re-read with `--fields` to confirm values landed.
7. **Metadata & attachments.** `pdf_meta.py --set-meta` writes Title/Author/Subject/Keywords (DocInfo); `--clear-meta` drops them; `--attach`/`--list-attachments`/`--extract-attachments` round-trip embedded files.
8. **Secure.** Encrypt with distinct user/owner passwords and AES-256. To remove a password you know, `--decrypt` writes an unencrypted copy.
9. **Verify** (see below) before reporting success.

## Pitfalls

- **Scanned PDFs**: empty `extract_text()` plus page images means there is no text layer. Route to `ocr-and-documents`; do not fabricate text.
- **Flattening limits**: `pdf_fill_form.py --flatten` uses pypdf's flatten support, which converts widget appearances into page content. It is reliable for plain text fields and checkboxes but can drop or misrender exotic widgets (rich text, custom appearance streams, some radio groups). Verify the flattened output visually with `vision_analyze`; for bulletproof flattening use an external renderer (e.g. Ghostscript or `pdftoppm`+reassembly) as a fallback.
- **NeedAppearances**: after filling, viewers only render values if appearance streams exist. The fill script sets the AcroForm `NeedAppearances` flag so conforming viewers regenerate them; some minimal viewers ignore it — flatten if display fidelity matters.
- **Non-Latin form values**: values are stored correctly (UTF-16), but the field's default font may lack glyphs, so a viewer can show blanks even though the data round-trips. Verify with `--fields`, not just visually.
- **Compression expectations**: `--compress` only deflates content streams. Typical savings are 0–20%; it does nothing for PDFs dominated by images or already-compressed streams. It is not a substitute for image downsampling (Ghostscript territory).
- **Permission flags don't enforce**: owner-password permission bits (no-print, no-copy) are polite requests that viewers may honor; any library (including pypdf) can read and strip them. Only the user password actually gates content via encryption. Never present permission flags as security.
- **Table extraction is heuristic**: pdfplumber detects tables from ruling lines/word alignment; borderless or merged-cell tables may need `table_settings` tuning or manual cleanup.
- **Page indexing**: helper CLIs take 1-based pages; pypdf APIs are 0-based. The scripts convert — don't double-convert.
- **Rotated stamp text extraction**: pdfplumber's line grouping scrambles rotated glyphs (a 45° "DRAFT" extracts as stray letters); verify rotated stamps with `pypdf`'s `extract_text()` or a rendered image instead.
- **Radio groups**: reportlab needs ≥2 `radio()` widgets per group, fills need the slashed export value (`"/red"`), and flatten fidelity is worst for radios — see `references/forms.md`.
- **Metadata scope**: `pdf_meta.py` writes the classic DocInfo dictionary only; embedded XMP metadata (if any) is left untouched and may show different values in some viewers.
- **PDF/A is out of scope**: pypdf/reportlab cannot produce or validate conformant PDF/A. If archival conformance is required, run Ghostscript via the `terminal` tool (e.g. `gs -dPDFA=2 -dPDFACompatibilityPolicy=1 -sColorConversionStrategy=UseDeviceIndependentColor -sDEVICE=pdfwrite -o out.pdf in.pdf` with a suitable ICC profile) and validate with veraPDF — both are external installs, and the result still needs validation, not assumption.
- Rotation must be a multiple of 90; encrypted inputs must be decrypted before any other operation.

## Verification

- After create/merge/split: `pdf_read.py out.pdf --meta` — confirm `page_count`, and per-page `rotation` when you rotated.
- After extraction: check the JSON is non-empty and spot-check a known string or cell.
- Form design loop: `pdf_form_layout.py spec.json` must exit 0; then `--render-overlay boxes.png --pdf form.pdf` and review the PNG with `vision_analyze` (red = entry boxes with field names, blue = label boxes) asking about overlaps, misalignment, and labels detached from their fields. Iterate spec → lint → overlay until clean.
- After building a form: `pdf_read.py form.pdf --fields` lists every spec field with the right type and options.
- After form fill: `pdf_read.py filled.pdf --fields` and compare values (exact match, including non-ASCII).
- After stamping: re-extract text (pypdf for rotated stamps) or render the page with `pdf_page_image.py` and inspect with `vision_analyze`.
- After metadata/attachment edits: `pdf_read.py --meta` / `pdf_meta.py --list-attachments`, and re-extract an attachment to byte-compare.
- After encrypt: `--meta` shows `"encrypted": true` and opening without a password fails; after decrypt, text extraction matches the original.
- For anything visual (watermarks, flattened forms), render and inspect with `vision_analyze`.

---

## Sub-Module: pdf-text-editing

# PDF Text Editing (in-place, PyMuPDF)

Surgically edit text inside an existing PDF — reorder sections, swap wording, renumber steps — while leaving images/figures exactly where they are. Works offline with PyMuPDF only (no nano-pdf LLM key, no re-render of the whole doc, so charts/screenshots survive bit-identical).

## When to Use

Use when the user asks to "edit / change / reorder" text in an existing PDF (a slide deck, manual, knowledge doc) AND the images must stay put. Use `nano-pdf` when the edit is one small wording change and an LLM key is available; use the `pdf` skill for create/merge/split/forms. This skill is for surgical text-layer surgery with layout control.

## Prerequisites

```bash
python3 -m venv ~/pdfenv && ~/pdfenv/bin/pip install pymupdf pypdf
# Windows host fonts for matching original fonts (WSL):
ls /mnt/c/Windows/Fonts/ | grep -iE "calibri|consola"   # calibri.ttf, calibrib.ttf, consol*.ttf
```

## Workflow

1. **Survey the page geometry first.** Extract per-page text (pypdf) to find the section to change, then get exact blocks/spans:
   ```python
   import pymupdf
   doc = pymupdf.open(src)
   page = doc[page_idx]  # 0-based
   for b in page.get_text("blocks"):        # (x0,y0,x1,y1,text,bno,btype)
       print(f"[{b[1]:6.1f}-{b[3]:6.1f}] x[{b[0]:5.1f}-{b[2]:5.1f}] {b[4][:70]}")
   for l in page.get_text("dict")["blocks"]:
       for s in l.get("lines", []):
           for sp in s["spans"]:            # origin=(baseline x,y), size, font, color
               print(sp["origin"], sp["size"], sp["font"], sp["text"])
   ```
2. **Map protected image regions.** `page.get_images(full=True)` + `page.get_image_rects(xref)` → the rects that must NOT be touched. Text captions like `[Gambar 12 — ...]` are TEXT, not images — safe to edit; the real figure is an image xref.
3. **Baseline-hash the images you must keep** (verification later):
   ```python
   clip = pymupdf.Rect(90, 238, 558, 592)   # exact image rect
   h_before = hashlib.md5(page.get_pixmap(clip=clip).samples).hexdigest()
   ```
4. **Redact old text:** one `add_redact_annot(rect, fill=False)` per old block bbox, then `page.apply_redactions()`. Keep rects strictly inside text areas — `apply_redactions` deletes ANY image overlapping a redact rect.
5. **Insert new text with matching fonts:** load Windows TTF so glyphs match the doc (Calibri, Calibri-Bold via `calibrib.ttf`, Consolas, italic via `calibrii.ttf`):
   ```python
   page.insert_font(fontname="calbf", fontfile="/mnt/c/Windows/Fonts/calibrib.ttf")
   page.insert_text((x, baseline_y), "Windows (WSL) — Install WSL Dulu",
                    fontname="calbf", fontsize=14, color=(0.145, 0.388, 0.922))
   ```
   Baseline y = old span's `origin[1]`; x = old span's `origin[0]`. Use original sizes (11 body, 10 code) and colors (read from span `color`).
6. **Save:** cannot `doc.save(src)` directly → `ValueError: save to original must be incremental`. Save to a temp file, then `shutil.move(tmp, src)` — plain `os.replace` fails cross-device on WSL→/mnt/c (`Invalid cross-device link`).
7. **Verify:**
   - image hash unchanged, `len(page.get_images())` same count
   - `page.get_text()` shows new content
   - re-check block rects: no new text overlapping image rects or the `Page N` footer
   - backup the original first (`shutil.copy2(src, bak)`)

## Pitfalls

- Redact rects must not overlap image rects — `apply_redactions` removes overlapping images, not just text.
- Space check before inserting: count free vertical room between existing blocks and the footer (`Page N` block). If the new content needs more lines than the gap, split content above and below the mid-page figure instead of squeezing.
- Reordering steps under a fixed figure: keep steps 1-2 above the image rect, steps 3+ below it; the figure stays at its original y-range.
- Colors are 0-1 floats in `insert_text`, not 0-255 hex; span `color` is already 0-1 int-packed — unpack with `(c>>16&255)/255, (c>>8&255)/255, (c&255)/255`.
- `execute_code` sandbox may have a different HOME → absolute venv path (`/home/<user>/pdfenv/bin/python`) breaks there; run the edit via `terminal` heredoc instead.
- Full working example (this exact WSL reorder flow): `references/pymupdf-text-edit.md`.
- Handing the edited PDF back to the user as an editable Word doc (pdf2docx, dropped-line/merged-paragraph/U+2010 repair): `references/pdf-to-docx-conversion.md`.
- **Inserted text round-trips wrong codepoints.** PyMuPDF `insert_text` with loaded TTF fonts writes U+2010 HYPHEN where you typed ASCII `-` (and the doc's own text uses ASCII). Any later extraction — docx conversion, copy-paste — carries the wrong codepoint (`wsl --install` becomes `wsl ‐‐install`). After any edit+extract cycle, grep the output for `\u2010` and normalize to `-`.

## Verification

1. `fitz` open output, hash-compare every image clip region against pre-edit hash.
2. Assert image count did not change.
3. Extract text, confirm old strings gone and new strings present.
4. Render `page.get_pixmap(dpi=100)` → PNG and inspect blocks/rects for overlaps (vision model may be unavailable — coordinate checks are sufficient).

---

## Sub-Module: nano-pdf

# nano-pdf

Edit PDFs using natural-language instructions. Point it at a page and describe what to change. For structural PDF work (merge, split, forms, watermarks, creation), see the `pdf` skill; for text extraction from scans, see `ocr-and-documents`.

## Prerequisites

```bash
# Install with uv (recommended — already available in Hermes)
uv pip install nano-pdf

# Or with pip
pip install nano-pdf
```

## Usage

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

## Examples

```bash
# Change a title on page 1
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"

# Update a date on a specific page
nano-pdf edit report.pdf 3 "Update the date from January to February 2026"

# Fix content
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

## Notes

- Page numbers may be 0-based or 1-based depending on version — if the edit hits the wrong page, retry with ±1
- Always verify the output PDF after editing (use `read_file` to check file size, or open it)
- The tool uses an LLM under the hood — requires an API key (check `nano-pdf --help` for config)
- Works well for text changes; complex layout modifications may need a different approach

---

## Sub-Module: ocr-and-documents

# PDF & Document Extraction

For DOCX: see the `docx` skill (create/edit) or use `python-docx` for structured reads.
For PPTX: see the `powerpoint` skill (full create/read/edit support).
For PDF manipulation (merge, split, forms, watermarks, creation): see the `pdf` skill.
This skill covers **text extraction from PDFs and scanned documents**.

> **Coming from a `read_file` EXTRACTION COVERAGE WARNING?** `read_file` auto-converts local PDFs but reads the text layer only; the warning footer lists the pages that yielded no text (scanned images). For a handful of pages, render + vision is fastest: `pdftoppm -jpeg -r 150 -f N -l N file.pdf /tmp/page` then `vision_analyze` each image. For bulk OCR of many pages, use marker-pdf below (Step 2).

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)

---