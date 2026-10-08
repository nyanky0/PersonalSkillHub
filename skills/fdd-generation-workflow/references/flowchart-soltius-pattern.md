# Flowchart Pattern: Soltius Swimlane Style

## Reference FDDs
Studied from: `/mnt/d/SOLTIUS/FDD/FDD/Baru/OneDrive_2_03-09-2026/` and `OneDrive_3_03-09-2026/`

- FDD - Payment Request V1.08.docx
- FDD - Barcode App 1.0.docx
- FDD - RFID Integration - 1.0.0.docx

## Style Specifications

### Layout
- **Swimlane horizontal**: USER (top), System (bottom)
- **Flow direction**: Left → Right (horizontal)
- **Canvas size**: ~1400×850 px
- **DPI**: 150

### Colors
```python
BLUE_HEADER = '#2E5C8A'   # Header bar & lane labels
WHITE = '#FFFFFF'         # Box fills
BLACK = '#000000'         # Borders & ADD-ON header
RED_ARROW = '#C00000'     # Cross-lane triggers (USER→System)
BLUE_ARROW = '#5B9BD5'    # Main flow arrows
```

### Shapes
| Element | Shape | Fill | Border | Notes |
|---------|-------|------|--------|-------|
| Header | Rectangle | BLUE_HEADER | Black | White text, bold |
| Lane label | Rectangle | BLUE_HEADER | Black | Vertical text, left side |
| Start/End | Oval/Stadium | WHITE | Black, 1.5px | |
| Process box | Rounded rect | WHITE | Black, 1.5px | |
| ADD-ON badge | Rectangle | BLACK | None | Inside process box, top |

### Process Box Structure
```
┌─────────────────────────┐
│ ████ ADD-ON ████        │ <- Black header, white text
│                         │
│  Step description       │ <- Main text, centered
│                         │
└─────────────────────────┘
```

### Arrows
- **Horizontal**: Blue, thin (1.2-1.3px), between boxes in same lane
- **Vertical (cross-lane)**: Red, thin, from BOTTOM of USER box to TOP of System box
- **Never diagonal**
- **Never penetrate box interiors** — arrows must touch edges only

## Common Pitfalls

1. **Wrong arrow start/end points**
   - BAD: `cross_down(ax, x, Y_USER, sy_pos)` — uses box TOP as start, passes X as Y
   - GOOD: `cross_down(ax, x, Y_USER + BOX_H, Y_SYS)` — starts from box BOTTOM

2. **Diagonal arrows** — never use, causes overlap
   - Always route cross-lane connections vertically

3. **Arrow penetration** — verify arrow endpoints are exactly at box edges
   - Top edge of box = y
   - Bottom edge = y + BOX_H
   - Left edge = x
   - Right edge = x + BOX_W

## Generator Code
See: `/tmp/fdd_ibt/scripts/gen_soltius_v3.py`

Generated flowcharts saved to: `/tmp/fdd_ibt/flowcharts_v5/`
- flow_siklus.png
- flow_pengadaan.png
- flow_inventory.png
- flow_emergency.png
- flow_approval.png
- flow_state.png
- flow_integrasi.png
- flow_arsitektur.png

---

## Draw.io Alternative (via `drawio-skill`)

Jika flowchart membutuhkan file editable `.drawio` untuk revisi manual klien/tim:
- Referensi format: [draw.io AI Generation](https://www.drawio.com/docs/reference/diagram-generation/) & [Style Reference](https://www.drawio.com/docs/reference/diagram-generation/style-reference/).
- Gunakan `<mxGraphModel adaptiveColors="auto">` dengan root cell `id="0"` dan layer default `id="1"`.

### Style Properties (Soltius Standard):
- **Swimlane Container**: `swimlane;horizontal=1;startSize=30;fillColor=#F8F9FA;strokeColor=#2E5C8A;strokeWidth=2;swimlaneFillColor=#FFFFFF;fontStyle=1;fontSize=12;fontColor=#FFFFFF;swimlaneLine=1;` (Header fill: `#2E5C8A`)
- **Process Box**: `rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=11;`
- **Decision Rhombus**: `rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=11;`
- **Start/End (Terminal)**: `ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=11;`
- **Cross-lane Trigger Arrow (Red)**: `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#C00000;strokeWidth=1.5;endArrow=classic;`
- **Main Flow Arrow (Blue)**: `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#5B9BD5;strokeWidth=1.5;endArrow=classic;`

