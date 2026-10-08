# fdd-generator

# FDD Generation from Codebase

Use when generating FDD (Functional Design Document) for SAP B1 add-on or web project based on existing Laravel/React/Vue codebase.

## Input

- Project root directory (Laravel + React/Vue)
- Target FDD title (e.g., "IBT Request Fulfillment v2.0")

## Process

1. **Codebase Analysis**
   - Extract routes (web.php/api.php) → main modules
   - Extract controllers/methods → feature list
   - Extract migrations/models → master data tables
   - Extract component hierarchy → UI pages

2. **Flowchart Generation (draw.io XML)**
   - Standard shapes (hasil studi 11 FDD Soltius + flowchart IBT):
     - `ellipse`: Start/End (`#E2EFDA`, `#548235`) — Gaya flat 1-lane
     - `rhombus`: Decision (`#FFF2CC`, `#BF9000`)
     - `rounded=1`: Process (`#DCE9F7`, `#4472C4`)
     - `rounded=1, E8DAEF`: SAP sync (`#7030A0`)
     - `rounded=1, FBE5E1`: Rejection path (`#C00000`)
   - **Alternatif Gaya Soltius swimlane** (FDD konsultan, cross-functional): shape white fill `#FFFFFF` border `#2E74B5`, lane horizontal User/SAP Business One/Add-On, Start/End stadium, badge sistem pojok kanan shape ("SAP"/"ABAP"/"Add On"), panah biru, label Yes/No. drawio: pakai `swimlane` container per role + `mxCell` child biasa.
   - Orthogonal edges, fontFamily=Helvetica, fontSize=11

3. **UI Mockup Generation (Tailwind HTML)**
   - Font: Caveat or Architects Daughter (handwritten)
   - Sketch aesthetic: dashed borders, gray placeholders, red "MOCKUP" badge
   - Standard components: sidebar nav, form cards, tables, stat cards
   - Indonesian labels where applicable

4. **Document Structure (docx)** — 4 varian ala Soltius:
   - **Client add-on SAP B1**: Bab 3 = Design Struktur Data (UDT + UDF per table [No/Field ID/Field Name/Type/Sub-Type/Size/Notes] + UDO + Validasi + Choose From Lists), UI = screenshot form asli, Bab 5 = blok Approval sign 2 pihak (SOLTIUS: QA/PM/Technical Consultant; CLIENT: PM/Manager/Staff).
   - **Web-based**: DB tables, approval mapping, sidebar UI mockup.
   - **Report-only** (PSAK118/IFRS16): read-only OJDT/JDT1, param filter, output report.
   - **Integrasi/FMS** (Payment Order): UDT/UDF/UDO + export bank.
   - H1: Pengenalan
     - H2: Latar Belakang Development
     - H2: List of Purposes
     - H2: Urutan Development (Product Backlog, Sprint Planning, etc.)
   - H1: Flowchart
     - H2: [Module] — [Process Name]
   - H1: User Interface
     - H2: [Page Name]
       - H3: [Section] (e.g., Form Fields, Table Columns, Actions)
   - H1: Approval
     - H2: [Approval Stage] — [Role] — [Conditions]
   - H1: SAP Integration
     - H2: [Sync Point] — [Object] — [Direction]
   - H1: Master Data
     - H2: [Table] — [Fields]

5. **Export**
   - docx → FDD-Project-vX.X.docx
   - flowcharts → flowcharts/drawio/*.drawio (svg/png exported later)
   - mockups → mockups/*.html (screenshot for preview)

## Template Snippets

### Flowchart Shape (draw.io XML)
```xml
<mxCell id="n1" value="Start" style="ellipse;whiteSpace=wrap;html=1;fillColor=#E2EFDA;strokeColor=#548235;fontSize=11;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="400" y="40" width="140" height="50" as="geometry"/></mxCell>
<mxCell id="n2" value="Decision?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#BF9000;fontSize=11;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="410" y="120" width="120" height="80" as="geometry"/></mxCell>
<mxCell id="n3" value="Process" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCE9F7;strokeColor=#4472C4;arcSize=20;fontSize=11;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="120" y="230" width="140" height="50" as="geometry"/></mxCell>
<mxCell id="n19" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;fontSize=9;fontFamily=Helvetica;" edge="1" parent="1" source="n1" target="n2"><mxGeometry relative="1" as="geometry"/></mxCell>
```

### UI Mockup (Tailwind HTML)
```html
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Architects+Daughter&display=swap" rel="stylesheet">
<style>
* { font-family: 'Architects Daughter', monospace !important; box-sizing: border-box; }
body { background: #f5f5f0; margin: 0; padding: 20px; }
.sketch { border: 2px dashed #999; background: #fff; border-radius: 8px; padding: 20px; position: relative; }
.sketch::before { content: 'MOCKUP — NOT FINAL DESIGN'; position: absolute; top: -12px; left: 20px; background: #ff6b6b; color: white; font-size: 10px; padding: 2px 10px; border-radius: 10px; font-family: 'Caveat', cursive; }
.box { border: 2px solid #555; border-radius: 4px; background: #f9f9f9; padding: 10px; margin: 8px 0; }
.placeholder { background: #e8e8e8; border: 1px dashed #aaa; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; color: #999; font-size: 12px; }
.label { font-family: 'Caveat', cursive; font-size: 16px; color: #444; }
.btn-sketch { border: 2px solid #444; border-radius: 6px; padding: 6px 16px; display: inline-block; font-size: 13px; color: #444; background: #f0f0f0; }
table.sketch-table { width: 100%; border-collapse: collapse; }
table.sketch-table td { border: 1px solid #ccc; padding: 6px 10px; color: #888; font-size: 12px; }
</style>
</head>
<body>
<div class="max-w-4xl mx-auto">
  <h1 class="text-2xl mb-4" style="font-family:'Caveat',cursive;">Mockup X.X — [Page Name]</h1>
  <div class="sketch max-w-md mx-auto">
    <!-- content -->
  </div>
</div>
</body>
</html>
```

### Docx Heading Structure (Python-docx)
```python
from docx import Document
doc = Document()
doc.add_heading('Pengenalan', level=1)
doc.add_heading('Latar Belakang Development', level=2)
doc.add_heading('List of Purposes', level=2)
doc.add_heading('Urutan Development', level=1)
doc.add_heading('Product Backlog', level=3)
```

## Pitfalls

- **Over-engineering UI**: Keep it wireframe-style, not production UI. Dashed borders, placeholders, red mockup badge.
- **Missing SAP sync points**: Cross-reference Service Layer endpoints or DI API calls for SAP integration points.
- **Inconsistent flowchart colors**: Stick to the palette: green (start/end), yellow (decision), blue (process), purple (SAP), red (rejection).
- **Indonesian vs English labels**: Use English for technical terms (Doc No, Status, Create, Submit) but Indonesian for page titles ("Halaman Login", "Daftar Transaksi").

## Examples

- `/mnt/d/SOLTIUS/FDD/FDD/FDD - Vendor Portal.docx` — similar structure for vendor portal add-on
- `/mnt/d/SOLTIUS/FDD/FDD/FDD - GRPO Service v1.2.docx` — process-focused FDD
- `/mnt/d/SOLTIUS/FDD/FDD/flowcharts/drawio/01-alur-umum-siklus-transaksi.drawio` — standard flowchart XML
- `/mnt/d/SOLTIUS/FDD/FDD/mockups/mockup-01-login.html` — mockup HTML template

## Verification

- Check flowchart XML validates with draw.io (open → save → no warnings)
- Check mockup renders in browser (no CSS errors)
- Check docx opens in Word (no corruption)
- Confirm all SAP sync points referenced from codebase are documented