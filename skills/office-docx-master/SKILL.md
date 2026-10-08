---
name: office-docx-master
description: "Master Microsoft Word (.docx) document generation and surgical editing via python-docx and docx-js."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [docx, word, report, python-docx]
---

# Office Docx Master



## Sub-Module: docx

# Docx Skill

Create, read, edit, and template Microsoft Word `.docx` files with
python-docx via small CLIs. It handles text, styles, lists, tables,
images, headers/footers, `{{token}}` templating, tracked changes
(list/accept/reject), comments (list/add/delete), TOC and page-number
fields, and package health checks. It does not render documents itself
(PDF needs LibreOffice — see Converting to PDF) or edit legacy `.doc`.

## When to Use

- The user asks to generate a Word document (report, letter, contract).
- You need the text, outline, styles, or embedded images of a `.docx`.
- You must change an existing `.docx`: replace text, edit table cells,
  insert/delete paragraphs, apply styles, merge fragmented runs.
- You have a `.docx` template with `{{placeholders}}` to fill from data.
- The document has tracked changes to review, accept, or reject.
- You need to read reviewers' comments, or add/delete comments.
- A `.docx` won't open or behaves oddly and you need corruption triage.
- The document needs a table of contents or "Page X of Y" footers.
- Not for: `.doc` (legacy), `.odt`, or WYSIWYG layout work.

### Soltius Corporate & Blueprint Document Patterns
- **Soltius FDD Documents**: Use standard paragraph styles `SOL-Level 1`, `SOL-Level 2`, `SOL-Par1`, `SOL-List`, and `SOL-Free` with `add_note_box()` for callouts. See [`fdd-generation-workflow`](../fdd-generation-workflow/SKILL.md) and [`sap-b1-fdd-author`](../sap-b1-fdd-author/SKILL.md).
- **Meeting Minutes & Blueprint Notes**: For transforming raw client notes into structured `.docx` deliverables with callout boxes (KESIMPULAN, PERTANYAAN TERBUKA) and action tables, see [`meeting-notes`](../meeting-notes/SKILL.md).

### Standard Table Typography & Spacing
- **Font**: `Cambria`
- **Font Size**: `11 pt`
- **Line & Paragraph Spacing**: `1.0` (Single line spacing, `space_before = Pt(0)`, `space_after = Pt(0)`)
- **Coloring**: Dipertahankan sesuai tema yang berlaku (misal: Black Table Style `#000000` header / `#FFFFFF` body).


## Prerequisites

- Python 3.10+ with `python-docx` installed:
  `pip install python-docx` (import name is `docx`; lxml comes with it).
- Comments `add` uses the native API on python-docx >= 1.2 and an XML
  fallback on older versions — both are automatic.
- For image blocks: the image files must exist locally (PNG/JPEG).

## How to Run

All helpers live in `scripts/` next to this file. Run them with the
`terminal` tool; each supports `--help` and prints JSON to stdout.

```bash
python scripts/docx_create.py spec.json out.docx
python scripts/docx_read.py out.docx --text
python scripts/docx_edit.py replace out.docx --find old --replace new
python scripts/docx_template.py tpl.docx values.json filled.docx
python scripts/docx_revisions.py list out.docx
python scripts/docx_comments.py list out.docx
python scripts/docx_validate.py out.docx
```

## Quick Reference

| Task | Command |
| --- | --- |
| Create from JSON spec | `docx_create.py spec.json out.docx` |
| Full text (body+tables+headers/footers) | `docx_read.py f.docx --text` |
| Heading outline + table shapes | `docx_read.py f.docx --structure` |
| Styles actually used | `docx_read.py f.docx --styles` |
| Extract embedded images | `docx_read.py f.docx --images outdir/` |
| Detect tracked changes/comments | `docx_read.py f.docx --revisions` |
| Find/replace (formatting kept) | `docx_edit.py replace f.docx --find A --replace B -o out.docx` |
| Set a table cell | `docx_edit.py set-cell f.docx --table 0 --row 1 --col 2 --text X` |
| Insert paragraph before index N | `docx_edit.py insert f.docx --index N --text X --style Normal` |
| Delete paragraph N | `docx_edit.py delete f.docx --index N` |
| Apply style to paragraph N | `docx_edit.py style f.docx --index N --style "Heading 1"` |
| Merge equal-format adjacent runs | `docx_edit.py normalize f.docx -o out.docx` |
| Insert TOC field before para N | `docx_edit.py toc f.docx --index N -o out.docx` |
| "Page X of Y" footer fields | `docx_edit.py page-numbers f.docx` |
| Fill `{{tokens}}` | `docx_template.py tpl.docx values.json out.docx --strict` |
| List revisions (id/author/date/text) | `docx_revisions.py list f.docx` |
| Accept / reject all revisions | `docx_revisions.py accept-all f.docx -o out.docx` (or `reject-all`) |
| Accept / reject one revision | `docx_revisions.py accept f.docx --id 3 -o out.docx` |
| List comments (+anchored text) | `docx_comments.py list f.docx` |
| Add comment anchored to text | `docx_comments.py add f.docx --target "phrase" --text "note" --author You` |
| Delete comment by id | `docx_comments.py delete f.docx --id 0` |
| Health-check the package | `docx_validate.py f.docx` (exit 1 on errors) |

## Procedure

1. **Create.** Write a JSON spec with `write_file`, then run
   `scripts/docx_create.py`. The spec supports: `page` (size + margins in
   mm), `header`/`footer` strings, `footer_page_numbers` (adds a
   "Page X of Y" field footer), `styles` (custom paragraph styles with
   font, size, bold/italic, hex `color`), and `blocks` — `heading`
   (level 1-9), `paragraph` (either `text` or a `runs` list where each run
   may set `bold`/`italic`/`underline`), `bullet_list`, `numbered_list`,
   `table` (`header` row rendered bold, `rows`, optional built-in table
   `style` such as `Table Grid`), `image` (`path`, optional `width_mm`),
   `toc` (Table of Contents field), and `page_break`. The full spec
   format is documented at the top of `scripts/docx_create.py`.
2. **Read.** Use `scripts/docx_read.py` with exactly one mode flag.
   `--text` returns body paragraphs, all table cell text, and
   header/footer text as JSON. `--structure` returns the heading outline
   plus paragraph/table/section counts. `--images DIR` copies every file
   under `word/media/` out of the package.
3. **Edit.** Use `scripts/docx_edit.py`. `replace` walks body, tables
   (nested included), headers and footers, and preserves run formatting;
   add `--body-only` to skip headers/footers. Pass `-o out.docx` to keep
   the original; omit it to edit in place. Paragraph indices for
   `insert`/`delete`/`style`/`toc` refer to `--structure`/`--text` body
   order. Run `normalize` first on documents that came out of heavy Word
   editing — it merges adjacent runs with identical formatting so later
   find-replace matches reliably.
4. **Review revisions.** `docx_revisions.py list` reports every `w:ins`
   and `w:del` (id, author, date, affected text) anywhere in body,
   tables, headers, or footers. `accept-all` / `reject-all` resolve them
   in bulk; `accept`/`reject --id N` handles a single revision. Accept
   keeps insertions and drops deleted text; reject does the reverse.
5. **Comments.** `docx_comments.py list` returns each comment's id,
   author, date, body text, and the document text it is anchored to.
   `add --target "some phrase"` anchors a new comment to the first
   occurrence of that phrase (runs are split as needed; formatting is
   preserved). `delete --id N` removes the comment and its markers
   without touching document text.
6. **Template.** Put `{{name}}`-style tokens in the document. Run
   `scripts/docx_template.py` with a JSON object of values. Use
   `--strict` to fail when tokens remain unfilled; the JSON output lists
   `filled` counts and `unfilled_tokens` either way.
7. **Verify** (always): re-read the output with `--text` or
   `--structure`, and run `docx_validate.py` on anything you produced
   via revision/comment surgery.

## Converting to PDF

No script needed. When LibreOffice is installed, convert headlessly:

```bash
soffice --headless --convert-to pdf --outdir outdir/ file.docx
```

Check availability first (`command -v soffice || command -v
libreoffice`). If neither exists, tell the user PDF conversion is
unavailable in this environment rather than improvising — python-docx
cannot render PDFs, and layout fidelity requires a real renderer.

## Pitfalls

- **Tokens split across runs.** Word often fragments text into several
  runs. The replace helpers collapse matched runs (replacement inherits
  the first run's formatting); running `docx_edit.py normalize` first
  reduces fragmentation for all later edits.
- **Revision coverage.** `docx_revisions.py` resolves run-level
  insertions and deletions (the overwhelming majority). Paragraph-mark
  and table-row revisions, format-change records, and moves are detected
  by `--revisions` but not auto-resolved — see
  `references/revisions-and-comments.md` and hand those to Word.
- **Comment threading.** Replies and "resolved" status live in
  `commentsExtended.xml`, which this skill ignores; comments it adds are
  plain top-level comments.
- **Field results are computed by Word.** `toc`, `page-numbers`, and the
  `toc`/`footer_page_numbers` spec options write *field codes*.
  Word/LibreOffice populates the actual entries and numbers when the
  file is opened (Word may prompt to update fields); python-docx never
  computes them, so placeholder text shows until then.
- **Validation is a health check, not schema validation.**
  `docx_validate.py` verifies the zip, required parts, relationship
  targets, image magic bytes, and referenced styles. It is NOT XSD
  validation — a file can pass and still contain XML Word dislikes.
- **Style names must exist.** Applying a style that isn't defined in the
  document raises `KeyError`. Built-ins like `Heading 1`, `List Bullet`,
  `List Number`, `Table Grid` exist in the default template; custom
  styles must be declared in the create spec first.
- **Numbered lists restart.** `List Number` relies on Word's default
  numbering; separate lists in one document may continue numbering
  instead of restarting. Warn users needing precise multi-list numbering.
- **Cell writes replace formatting.** `set-cell` uses `cell.text = ...`,
  which resets runs in that cell to plain formatting.
- **Encoding.** All JSON specs/values files are read as UTF-8 explicitly;
  never rely on locale defaults when writing your own glue code.
- **Don't unzip-and-sed the XML.** Edit through the scripts (or
  python-docx); raw text substitution in `document.xml` corrupts files
  easily. Use `patch`/`write_file` only for the JSON inputs, never on the
  `.docx` itself.

## Verification

- After create/edit/template, run `docx_read.py out.docx --text` and
  check the expected strings appear (and old strings are gone).
- After accept/reject, `docx_revisions.py list` should return `[]` (or
  only the ids you intentionally left); after comment surgery,
  `docx_comments.py list` should reflect the change and `--text` output
  must be unchanged.
- `docx_validate.py out.docx` exits 0 with `"ok": true` on a healthy
  package — run it after any revision/comment/field manipulation.
- For templates run with `--strict`, or check `unfilled_tokens == []`.
- Structure checks: `--structure` should show the expected heading
  outline and table shapes; `--styles` confirms custom styles applied.

---

## Sub-Module: docx-creation

# DOCX Creation Skill

Use when generating complex .docx documents via Node.js with docx-js library.

## When to Use

Use this skill when generating Word documents programmatically using `docx-js` library via Node.js scripts, especially when:
- Document exceeds tool call token limits
- Need to merge multiple generated .docx files
- Working with large tables, multiple sections, or dynamic content

## Prerequisites

```bash
npm ls docx --depth=0 2>/dev/null || npm install docx
npm ls jszip --depth=0 2>/dev/null || npm install jszip
```

## Quick Reference

| Task | Approach |
|---|---|
| Single small doc | One script (under ~8KB) |
| Large doc | Split into helpers.js + partN.js chains |
| Merge docx | Use JSZip to extract body XML → concatenate |
| Table cells | `width: { size: N, type: WidthType.DXA }` |
| Shading | Use `ShadingType.CLEAR`, never `SOLID` |

## Multi-Part Generation Pattern

### helpers.js
```javascript
const { W, heading, cellHeader, cellValue, emptyCell, tableRows } = require("./helpers");

module.exports = { W, heading, cellHeader, cellValue, emptyCell, tableRows };
```

### part1.js
```javascript
const { run } = require("./part2");
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(path.join(outDir, "Part1.docx"), buffer);
  require("./part2").run(...);
});
module.exports = { run };
```

### partN.js
```javascript
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(path.join(outDir, "PartN.docx"), buffer);
});
module.exports = { run };
```

## Merging .docx Files

Use JSZip to unzip → extract body XML → concatenate → re-zip. Or use the bundled script:

```bash
node scripts/merge-docx.js part1.docx part2.docx part3.docx -o merged.docx -d /output/dir/
```

## API Pitfalls

1. **`TableCell` width must be object, not number**: `width: { size: N, type: WidthType.DXA }`
2. **Export all helper functions** needed by downstream parts
3. **ShadingType.CLEAR**, never SOLID (renders black)
4. **Module.exports pattern**: `module.exports = { run }`, not `null`

## Related Skills

- `docx` — read, edit, render Word documents
- `pdf` — PDF work, validation via render

## Verification

1. Check file opens in Word without corruption
2. Verify table borders and shading render correctly
3. Verify page count matches expectation

---

## Sub-Module: python-docx-editing

# Python-docx Editing of Existing .docx

Surgical edits to existing Word docs (fix stale text, replace values, insert new sections) with `python-docx`, keeping all images and run formatting intact. Alternative to the bundled `docx` skill's raw XML surgery (unzip → merge_runs → edit document.xml → rezip) — use python-docx when edits are paragraph-level and you want to preserve the file as-is. Use the bundled docx skill for tracked changes, comments, or full-document rebuilds.

## When to Use

User asks to fix/update/review an existing .docx (change model names, correct a note, insert a new section, rework a paragraph) without rebuilding it. Triggers: "perbaiki docx", "update dokumen", "insert section in docx".

## Prerequisites

`python-docx` lives in the PDF venv on this machine (installed once; reinstall after venv rebuild):
```bash
~/pdfenv/bin/pip install python-docx
```

## Workflow

1. **Map paragraphs first.** Load `docx.Document(path)`, print index + style + text for paragraphs matching keywords. Some paragraphs have `style=None` — use `p.style.name if p.style else None`. Inspect run formatting (`r.font.name`, `r.font.size`, `r.bold`) of a heading + body + code paragraph to copy for new content. Typical doc pattern: headings Calibri 12 bold, body Calibri 14, code Consolas 11, `CATATAN:` prefix bold.
2. **Replace text in place** — `p.runs[0].text = new`. Keeps run formatting. Only touch run 0 when the paragraph is single-run.
3. **Insert new paragraphs** — `anchor.insert_paragraph_before()` then `p.add_run()` per run with explicit `font.name` / `font.size` / `bold`. Build runs as `(text, font, size_pt, bold)` tuples; a helper `make_para(anchor, runs)` keeps it uniform.
   No `insert_paragraph_after()` exists — to insert AFTER an anchor, build the `w:p` element and use `anchor._p.addnext(p_el)`, wrapping with `Paragraph(p_el, anchor._parent)`:
   ```python
   from docx.text.paragraph import Paragraph
   p_el = docx.oxml.shared.OxmlElement('w:p')
   anchor._p.addnext(p_el)
   p = Paragraph(p_el, anchor._parent)
   run = p.add_run("curl -fsSL https://... | bash")
   run.font.name = "Consolas"; run.font.size = docx.shared.Pt(10)
   rpr = run._element.get_or_add_rPr(); rf = rpr.get_or_add_rFonts()
   rf.set(docx.oxml.ns.qn('w:ascii'), "Consolas")   # code fonts need BOTH ascii+hAnsi
   rf.set(docx.oxml.ns.qn('w:hAnsi'), "Consolas")
   ```
4. **Split a merged paragraph** (lines collapsed into one para with `\n`, e.g. `'hermes setup \n5. Jalankan Hermes:'`): clear all runs (`r._element.getparent().remove(r._element)`), rebuild the first line's run, then `addnext()` a new paragraph for the remaining lines.
4. **Save to a NEW filename** (`..._v2.docx`), never over the original — Windows apps hold locks on Desktop files (`cp: cannot remove Permission denied`); write fresh name, verify, then let user decide.

## Pitfalls

- **run.text includes leading whitespace.** Replacing `p.runs[0].text` with text that drops the original leading spaces silently destroys YAML/code indentation (2-space/4-space indents vanish, snippet looks broken). Always re-prefix the exact original indent: `'  default: "x"'` not `'default: "x"'`. This bit hard on config.yaml snippets inside docs.
- **Normalize U+2010 HYPHEN to ASCII `-`** in every run after converting a PyMuPDF-edited PDF to docx — PyMuPDF `insert_text` writes U+2010 where the doc uses ASCII `-`, so commands like `wsl --install` arrive as `wsl ‐‐install`. One pass over all paragraphs: `r.text.replace('\u2010', '-')`.
- **Match paragraphs by exact `p.text`** for idempotent re-edits, but remember paragraph indices shift after insertion — re-scan after any insert.
- **Image count check is a false alarm.** python-docx drops the `word/media/` directory entry but keeps all real images. Verify with zipfile: compare `word/media` members vs original; `{n.split('/')[-1] for n in names if n.startswith('word/media')}` may show `''` (dir entry) as "missing" — that's normal. All real `.png` files stay referenced.
- `python-docx` round-trip preserves everything untouched; only the paragraphs you edit change.

## Paging / Layout Fix ("paging ngaco")

"Edit paging" = normalize a docx whose page layout is broken. Render → diagnose → fix → re-render.

1. **Render with real Word first** (LibreOffice/soffice may be absent). Word COM from WSL:
   ```powershell
   powershell.exe -NoProfile -Command "
   \$w = New-Object -ComObject Word.Application; \$w.Visible = \$false; \$w.DisplayAlerts = 0
   \$doc = \$w.Documents.Open('C:\path\file.docx', \$false, \$true)   # ReadOnly=true
   \$doc.ExportAsFixedFormat('C:\path\check.pdf', 17)                 # 17 = wdExportFormatPDF
   \`\$doc.Close(\$false); \$w.Quit()"
      ```
      Re-runnable version: `scripts/render_docx_to_pdf.ps1` (param SrcDocx, OutPdf; ReadOnly open).
      CRITICAL: Word COM cannot see WSL paths
   If the target docx is open in the user's Word, COM hangs on an invisible dialog → kill the stuck WINWORD pid (`Get-Process WINWORD` / `Stop-Process -Id`) but never the windowed one (MainWindowTitle set).
2. **Diagnose from the rendered PDF** (pymupdf): per page print page rect (`612x792` = Letter vs `595x842` = A4), text block y-ranges, and image rects. Symptoms to look for: mixed page sizes across sections, near-empty pages, images clipped short (img height a few pt), content overflowing footer, footer formats differing per page (`Page N of M` vs `1 | P a g e`).
3. **Fix with python-docx:**
   - Mixed sizes: set EVERY section to the same page: `s.page_width = Mm(210); s.page_height = Mm(297)` (A4) + uniform margins `Inches(1)`, header/footer distance `Inches(0.5)`.
   - Images wider than content: for each `w:drawing`, `wp:extent` cx in EMU (`914400`/inch); scale cx>MAXW down proportionally (`ext.set('cx', ...)` / `('cy', ...)`).
   - Inconsistent footers (`footer1.xml` vs `footer2.xml`): remove all `w:footerReference`/`w:headerReference` from every `w:sectPr` → all sections inherit the default (empty) footer.
   - Python-docx cannot open a docx locked by an open Word (`PackageNotFoundError`) — copy to WSL home first (`cp` from /mnt/c/Desktop usually works read-only), edit the copy, save fresh name.
   - Verify after: re-render to PDF and check page sizes uniform, no near-empty pages.

## Creating new .docx from scratch (FDD/report generation)

python-docx can build a full multi-chamber document from scratch — alternative to the `docx` skill's docx-js (npm) path. Use when the document needs embedded matplotlib charts/flowcharts/mockups and Python is the available toolchain. For full FDD generation workflow (codebase → draw.io flowcharts + HTML mockups + docx), see `references/fdd-generation-patterns.md`.

### Setup

```bash
# python-docx lives in the PDF venv on this machine
~/.venvs/pdf/bin/python -c "from docx import Document; print('ok')"
```

### Pattern

```python
import sys
sys.path.insert(0, "/home/maulana/.venvs/pdf/lib/python3.12/site-packages")
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3)
    section.right_margin = Cm(2.5)

def add_heading(text, level=1):
    return doc.add_heading(text, level=level)

def add_para(text, bold=False, italic=False, size=11, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = 'Calibri'
    if align: p.alignment = align
    return p

def add_bullet(text, prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if prefix:
        r = p.add_run(prefix); r.bold = True; r.font.size = Pt(11); r.font.name = 'Calibri'
    r2 = p.add_run(text); r2.font.size = Pt(11); r2.font.name = 'Calibri'
    return p

def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'  # NOT WD_TABLE_STYLE — doesn't exist in python-docx
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]; cell.text = h
        for p in cell.paragraphs:
            for r in p.runs: r.bold = True; r.font.size = Pt(9); r.font.name = 'Calibri'
    for row_data in rows:
        row = table.add_row()
        for i, val in enumerate(row_data):
            cell = row.cells[i]; cell.text = str(val) if val else '-'
            for p in cell.paragraphs:
                for r in p.runs: r.font.size = Pt(9); r.font.name = 'Calibri'
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows: row.cells[i].width = Cm(w)
    return table

def add_image(path, caption, width=6.2):
    if os.path.exists(path):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Inches(width))
        cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(caption); r.italic = True; r.font.size = Pt(9); r.font.name = 'Calibri'
    else:
        add_para(f"[GAMBAR: {caption} tidak ditemukan]", italic=True, size=9)

# Build: cover → page break → chapters → save
doc.save("output.docx")
```

### Pitfalls (creation)

- **`WD_TABLE_STYLE` import doesn't exist.** `from docx.enum.table import WD_TABLE_STYLE` → ImportError. Use `table.style = 'Table Grid'` (string) directly.
- **Emoji glyphs missing from DejaVu Sans.** When generating matplotlib mockups/wireframes, Unicode emoji (👤 📊 ✅ etc.) render as blank boxes with UserWarning. Use text labels or ASCII symbols instead.
- **Calibri in matplotlib ≠ Calibri in docx.** python-docx can set `font.name = 'Calibri'` fine (Word renders it). But matplotlib + Calibri `.ttf` from Windows Fonts is a variable font that renders nondeterministically. Keep matplotlib on DejaVu Sans, use Calibri only in docx text.
- **Soltius FDD house style** — when matching ref docs under /mnt/d/SOLTIUS/FDD/FDD/Baru/: see `references/soltius-fdd-visual-style.md` (3 flowchart dialects: RFID blue swimlane #4F88BA verb-labeled arrows; Work Order monochrome swimlane w/ parallelogram; Barcode flat light-blue #5A9AD4 w/ explicit Yes/No) + template gaps (header logo band, "N of M" footer, post-flowchart `No|Title|Description` tables).
- **Full FDD generation workflow** (codebase → draw.io flowcharts + HTML mockups + docx): see `references/fdd-generation-patterns.md` for orthogonal edge routing, shape conventions (ellipse vs rounded rect), vision check workflow (kimi-k3 via 9router direct curl), edge label positioning fix (near source exit, not midpoint; L-shaped label clamp outside target), node y-alignment for clean No-paths (Rejected box must match diamond center y), Z-route→L-shape conversion, arrowhead direction fix, wireframe sketch mockup style (customer demo/pre-final), and iterative render→vision→fix loop.
- **Flowchart shapes**: Start/End = ellipse (green=success, red=error). Rejected/Return = rounded rect (NOT ellipse — ellipse reserved for terminal). Process = rounded rect. Decision = diamond. See references for full color table.
- **Vision check for flowcharts**: kimi-k3 via 9router direct curl with base64 image. vision_analyze/browser_vision return 502. See references/fdd-generation-patterns.md → "Vision check workflow (kimi-k3 via 9router)".
- **Iterative flowchart QA**: render → vision check → fix .drawio source → re-render → re-vision. Typically 3+ rounds. Resize to max 800px width for vision. Short prompt = better response rate. Placeholder text ("[Daftar isi akan ter-generate...]") does NOT auto-generate — user must manually create the TOC. Instead, insert a real TOC field via OxmlElement so Word auto-populates on "Update Field":
  ```python
  from docx.oxml import OxmlElement
  from docx.oxml.ns import qn

  def add_toc_field(doc):
      p = doc.add_paragraph()
      run = p.add_run()
      fldChar1 = OxmlElement('w:fldChar')
      fldChar1.set(qn('w:fldCharType'), 'begin')
      instrText = OxmlElement('w:instrText')
      instrText.set(qn('xml:space'), 'preserve')
      instrText.text = ' TOC \\o 1-3 \\h \\z \\u '
      fldChar2 = OxmlElement('w:fldChar')
      fldChar2.set(qn('w:fldCharType'), 'separate')
      fldChar3 = OxmlElement('w:t')
      fldChar3.text = "Klik kanan > Update Field untuk generate Daftar Isi."
      fldChar4 = OxmlElement('w:fldChar')
      fldChar4.set(qn('w:fldCharType'), 'end')
      run._r.append(fldChar1)
      run._r.append(instrText)
      run._r.append(fldChar2)
      run._r.append(fldChar3)
      run._r.append(fldChar4)
  ```
  This produces a real Word TOC field that populates from Heading 1-3 styles on first "Update Field" (right-click → Update Field, or Ctrl+A then F9).
- **Headings: NO manual numbers.** `doc.add_heading("Pendahuluan", level=1)` — Word auto-numbers from the Heading style. Do NOT write `doc.add_heading("1. Pendahuluan", level=1)` — the "1. " prefix is a literal string that appears in the TOC and breaks auto-numbering. Just pass the title text; Word generates "1", "1.1", "1.1.1" from heading level hierarchy.
- **Embed images at Inches(6.2)** for full-width on A4 with 3cm left margin. Smaller for inline.
- **PermissionError on save.** If the target .docx is open in Windows Word, `doc.save()` raises `PermissionError: [Errno 13]`. Write to a different filename (e.g. v1.1 instead of v1.0) and let user close Word + rename later.

### Iterative rebuild from consolidated notes (FDD v2.0 pattern)

When user has a consolidated notes document and asks to simplify/update existing FDD ("semprunakan FDD"):

1. **Gap analysis first** — compare notes vs existing FDD. Classify each note item as MISMATCH / PARTIAL MATCH / MATCH. See `references/fdd-generation-patterns.md` → "14 FDD content gaps" and meeting-notes skill → `references/ibt-fdd-v2-gap-analysis.md` for a worked example (15 items, 11 mismatch, 3 partial, 1 match).
2. **Decide: patch vs rebuild** — kalau banyak MISMATCH (>5) atau struktur FDD berantakan, rebuild lebih cepat dan bersih. Kalau sedikit, patch surgical via `insert_paragraph_after()` pattern.
3. **Rebuild workflow**:
   - Start fresh `Document()` with python-docx
   - Cover + Disclaimer + TOC field (use `add_toc_field()` helper) + Bab 1-5
   - Scope section: group by module/feature — jangan perpanjang per-fitur satu-satu tanpa grouping
   - Bab 3: 1 master transactions table dengan module discriminator, bukan tabel terpisah per modul
   - Bab 3: UDF table terpisah, Validasi terpisah, Role-Based Access table terpisah
   - Bab 4: UI pages grouped by function
   - Bab 5: signature block
4. **Keep it lean**:
   - Consolidate fields: 1 transactions table with module discriminator (rl_type, rl_flag, etc.) instead of separate header tables per module
   - Remove overengineered features not in notes (2FA, QR verify, webhook logs, sap_draft_entry)
   - Error codes: keep only rule-based ones (100xx for app, 200xx for SAP)
5. **Verification**: `soffice --headless --convert-to pdf` + `pdfinfo Pages` + `pdftotext | grep` heading check. 29 pages is reasonable for a full web add-on FDD.

Script template: see `scripts/gen_fdd_docx.py` pattern (write to /tmp, execute with ~/.venvs/pdf/bin/python).

### Full FDD generation workflow (from codebase)

When generating a Functional Design Document (or similar multi-chapter doc) from a codebase:

1. **Extract** — read source code (migrations, models, controllers, configs, services) to understand tables, fields, business logic.
2. **Generate flowcharts** — PREFER draw.io XML (`.drawio` files) over matplotlib. See "Flowchart generation (draw.io)" below. Use matplotlib only as fallback.
3. **Generate mockup UIs** — PREFER HTML+Tailwind from actual JSX source over matplotlib wireframes. See "Mockup UI generation (HTML)" below.
4. **Assemble docx** — python-docx: cover → disclaimer → TOC field (use `add_toc_field()` helper, NOT placeholder text) → chapters with embedded images + tables → save.
5. **Verify** — check file size > 0, open with `read_file` or vision_analyze.

Script template: see `scripts/gen_fdd_docx.py` pattern (write to /tmp, execute with ~/.venvs/pdf/bin/python).

## Multi-part build + merge (long docs: FDD, manuals)

A 35+ page doc does not fit in one write_file call — content truncates. Split the builder into
`build_partA.py` / `build_partB.py` / `build_partC.py` sharing one `fdd_common.py` helper module,
each saving `_partA.docx` etc., then merge.

**MERGE WITH `docxcompose`, NEVER raw XML body copy.**

```python
from docx import Document
from docxcompose.composer import Composer   # ~/.venvs/pdf/bin/pip install docxcompose
master = Document('_partA.docx')
c = Composer(master)
for p in ['_partB.docx', '_partC.docx']:
    c.append(Document(p))
# page-number footer must be added AFTER merge (composer brings sections along)
# for sec in master.sections: add PAGE w:fldChar footer
master.save('FINAL.docx')
print('inline images:', len(Document('FINAL.docx').inline_shapes))
```

- **Silent image loss trap.** `copy.deepcopy(sub.element.body children)` into master looks
  successful — `len(doc.inline_shapes)` still reports the full count — but every `w:drawing`
  r:embed points at the sub-document's relationships, which were not copied. Result: captions
  render, image areas are BLANK pages in the converted PDF. `inline_shapes` count is NOT a valid
  image check after a manual merge.
- Hand-rolled relationship fixups fail too: `ImagePart.from_image(blob, None)` raises
  `'bytes' object has no attribute 'content_type'`; `master.part.relate_to()` cannot adopt a part
  owned by another package. Do not spend iterations here — install docxcompose.
- **After a docxcompose merge, verify images via `zipfile`, not `inline_shapes`:** open the merged
  file, list `word/media/*`, expect image count == the number you embedded (e.g. 8 flowcharts + 6
  mockups = 14). This catches missing rels even when python-docx still counts shapes.

### Figures with built-in captions (rework pitfall)

When flowchart/mockup PNGs carry their own caption INSIDE the image (Soltius ref style: "Gambar
X.Y — ..." bottom band), do NOT also add a python-docx caption paragraph under the image — the
caption renders twice. Reference the figure in surrounding prose by its internal number instead
("...tercakup pada Gambar 3.4 di sub-bab 3.3"). Conversely, plain UI screenshots have no internal
caption → keep the docx caption paragraph for those.

When swapping an old figure set for a reworked one, re-map EVERY `img(doc, ...)` call to the new
file AND its chapter: new charts rarely keep the old sub-bab numbering (e.g. one old swimlane
"3.5" may split into emergency "3.5" + approval "3.6"). Dump old-vs-new by reading the generator
source — `grep -n "cap(h" gen_*.py` lists each figure's internal caption; trust the source over
vision, which hallucinates node text at PDF-render resolution.

## Verify a generated docx (mandatory loop)

1. `libreoffice --headless --convert-to pdf FILE.docx --outdir pdfcheck` then `pdfinfo | grep Pages`.
2. `pdftotext -f 1 -l N out.pdf - | grep -n "^Gambar\|^Tabel"` — cheap structural check that figure
   captions AND headings survived.
3. `pdftoppm -png -r 130 -f P -l P out.pdf pg` + vision-check image-bearing pages.
   **Render at ≥130 dpi.** At 60 dpi vision calls diagram text "blur/unreadable" and hallucinates
   typos ("Puchasing", "migrastik") that are not in the source.
4. When vision reports odd wording, `grep` the generator source before "fixing" it — low-dpi OCR
   invents errors. Trust the source, not the OCR.
5. **Vision hallucinates node text at small scale — use it for STRUCTURE only.** Across renders at
   80 dpi and on 2x2 contact sheets, vision consistently fabricated node labels (invented MRP/PO
   flows, wrong company names "PT XYZ", wrong dates) while reliably answering: is there a chart, is
   it one page, is it clipped, does a caption exist, is the layout rapi. Ask binary layout questions
   ("utuh? terpotong? rapi?"); never trust its reading of what a node says — verify content from the
   generator source.
6. Deterministic checks beat vision where possible: find image-bearing PDF pages by pixel statistics
   (colored-pixel ratio via numpy) and confirm embedded image count with `zipfile` on the docx.

## Verify

```bash
# zip integrity + image count vs original
python3 -c "
import zipfile
for f in ['ORIG.docx','NEW.docx']:
    z = zipfile.ZipFile(f)
    imgs = [n for n in z.namelist() if n.startswith('word/media')]
    print(f, 'zip OK' if z.testzip() is None else 'BAD', len(imgs))
"
```
Then re-extract text (`read_file` on the new .docx) and eyeball: new section present at right spot, code/YAML indent intact, no text mangled. `soffice` render + vision check is optional (vision may be unconfigured on this machine).

---

## Sub-Module: word-report-docx

# Laporan Word (.docx) yang rapi & reproducible

## Kapan dipakai

User minta "dokumentasi / laporan / manual dalam bentuk Word yang enak dilihat". Jangan susun .docx satu-satu
secara manual — buat **script generator** (python-docx) supaya isi bisa di-update dan di-regenerate.
Prasyarat: `pip install python-docx`.

## Aturan inti

1. **Satu helper gaya + satu script per dokumen.**
   - `docs/laporan/word_style.py` → class `Doc` (cover, heading, paragraf, bullet/numbered, tabel berwarna,
     callout, daftar isi manual, footer nomor halaman).
   - `docs/laporan/build_0X_<topik>.py` → import `Doc`, tulis isi, `d.save(OUT)`.
   - Simpan generator **di repo** bersama .docx-nya; di guide tulis "jangan edit .docx langsung — edit build
     script lalu regenerate".
2. **Pecah jadi beberapa file kecil.** `write_file` konten >±8K token bisa putus di tengah stream.
   Satu script = satu dokumen.
3. **Verifikasi hasil, jangan hanya percaya exit code 0.** Buka balik dengan python-docx:
   `Document(f)` → cetak `len(d.paragraphs)`, `len(d.tables)`, jumlah sel; cek 3–5 paragraf pertama (judul
   cover) dan jumlah tabel sesuai rencana isi.
4. **Isi harus akurat & bisa ditelusuri.** Tiap klaim status (SELESAI / SEBAGIAN / BELUM) butuh bukti kode
   (grep, migrasi, keluaran skrip). Yang belum diperiksa → tulis "PERLU VERIFIKASI", jangan ditebak.

## Style yang dipakai (dan kenapa)

- Warna aksen biru korporat + netral slate; font Calibri/Segoe UI; header tabel berwarna aksen, teks putih.
- Kolom status diberi warna sel sendiri (hijau = selesai, kuning = sebagian, merah = belum) supaya pembaca
  bisa memindai tanpa membaca.
- Cover: label kecil (organisasi · jenis laporan), judul besar, subjudul, meta (versi/tanggal).
- Daftar isi ditulis manual sebagai daftar bernomor (bukan field TOC) agar langsung terlihat tanpa F9.
- Callout = kotak berisi satu paragraf tegas untuk peringatan/info penting.
- Lebar kolom tabel dijumlahkan ±16,5 cm (A4, margin 2,5 cm) supaya tidak meluber.

## Bahasa & nada dokumen

Dokumen deliverable memakai bahasa formal dan padat — **bukan** gaya obrolan persona. Kalimat datar, istilah
konsisten, tanpa basa-basi. (Persona chat hanya untuk balasan ke user.)

## API helper

- `d.h1/h2/h3(teks)`, `d.p(teks)`, `d.bullets([...])`, `d.numbered([...])`, `d.page_break()`
- `d.table(headers, rows, widths=[cm...], status_col=i)` — kolom status otomatis berwarna
- `d.callout(judul, isi, "warn"|"info")`, `d.toc([...])`, `d.save(path)`
- Teks mendukung penanda `**tebal**` sederhana.

Template helper siap pakai: lihat `templates/word_style.py` pada skill ini.

---

## Sub-Module: mermaid-to-docx

# Mermaid → PNG → Word .docx

Word cannot render Mermaid markup. When a deliverable (FDD, user manual,
proposal) needs flowcharts that display INSIDE the .docx, render each Mermaid
block to PNG via the free mermaid.ink API, then embed with python-docx.

## When to Use

- Generating a Word document that must show flowcharts/sequence diagrams
  inline (not as raw text the reader has to paste into mermaid.live).
- FDD / technical documentation for SAP B1 or any system where a Mermaid
  block was previously dumped as monospace text and the user asked for real
  images.
- Any docx spec with a `mermaid` block type that needs visual rendering.

## How to Run

1. Collect the Mermaid blocks (from your generator source, a spec file, or a
   doc). Each block is the triple-quoted string after `add_mermaid(doc, """`.
2. Render each block with `scripts/render_mermaid.py`:
   ```bash
   python scripts/render_mermaid.py flows.json out_dir/
   ```
   `flows.json` = `["flowchart TD\n A-->B", ...]` (list of Mermaid sources).
   Output: `flow1.png .. flowN.png` in `out_dir/`. Uses mermaid.ink, retries
   once, sleeps 0.4s between calls. Exit non-zero lists failures.
3. Embed in python-docx:
   ```python
   doc.add_picture(png_path, width=Mm(155))
   doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
   ```
   Keep a caption line above ("Gambar 2.1.1 ...") for figure numbering.
4. Verify: extract images back from the .docx (`docx_read.py out.docx
   --images dir/`) and confirm count = logos + diagrams.

## mermaid.ink API (the core trick)

- Endpoint: `https://mermaid.ink/img/<urlsafe_base64(payload)>`
- Payload is JSON: `{"code": "<mermaid>", "mermaid": {"theme": "default",
  "themeVariables": {"fontFamily": "Helvetica"}}}`
- Base64 must be URL-safe (replace `+`/`/` with `-`/`_`, strip `=`).
- Response is the PNG bytes; treat <200 bytes as failure (HTML error page).
- Alternative endpoint (less reliable, was 400 in testing): kroki.io.
- No API key needed; works over plain HTTPS from Python stdlib.

## Fallback (no network / render fails)

Keep the Mermaid block as monospace text (Consolas, ~8.5pt, one line per
paragraph, zero spacing between lines) plus the caption. Tell the user they
can paste into mermaid.live, or ask to retry rendering later.

## Pitfalls

- **MSYS path trap on Windows (git-bash)**: native python/curl interpret
  `/c/tmp/...` as `C:\c\tmp\...`. Always pass `C:/tmp/...`-style paths to
  python and curl; the bash shell's `/c/...` forms are for bash builtins.
- **Payload size**: keep diagrams small (under ~2KB source) — big payloads
  time out on mermaid.ink.
- **Emoji/kaomoji in labels**: fine in JSON, but keep them out of Mermaid
  node text if you ever fall back to text rendering (monospace width breaks).
- **Word figure numbering**: match caption numbers to subsection order
  (Gambar 4.1.1 = section 4.1.1) so the DAFTAR ISI / figure list stays
  consistent.
- **Docx validation**: after embedding, run `docx_validate.py` on the result
  — a bad image relationship fails silently in Word but is caught there.

## Verification

- `docx_read.py out.docx --images dir/` returns one PNG per embedded image;
  compare count with expected (cover logo + N diagrams).
- Open the docx in Word/LibreOffice: diagrams must appear, centered, with
  captions, no broken-image placeholders.

---