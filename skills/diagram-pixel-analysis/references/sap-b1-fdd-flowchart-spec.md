# Soltius FDD Flowchart Visual Spec

Verified via pixel analysis on 6 reference PNGs in `/mnt/d/SOLTIUS/FDD/FDD/flowcharts/`.
Method: PIL + numpy BFS connected components, no vision model (kimi-k3 backend was down).

## Node types (verified across all 6 flowcharts)

| Node type | Shape | Fill hex | Stroke hex | Pixel signature |
|---|---|---|---|---|
| Start/End | rect, SHARP corner (rx=0) | `#f0e0e0` (pink) | `#c00000` (red) | red fill 25k-85k px, red stroke ~1k px |
| Process | rect, SHARP corner | `#d0e0f0` (light blue) | `#4070c0` (blue) | blue fill 115k-236k px (dominant), blue stroke 8k-19k px |
| Decision | DIAMOND | `#f0f0c0` (pale yellow) | `#b09000` (gold) | yellow fill 17k-71k px, gold stroke 1.4k-4.7k px |
| SAP result | rect, SHARP corner | `#e0d0e0` (light purple) | `#8050b0` (purple) | purple fill 25k-103k px, purple stroke 0-1.7k px |
| Alt/secondary | rect, SHARP corner | `#f0e0c0` (pale orange) | TBD | orange fill 17k-71k px — appears in flowcharts 01,03,05 but not 02,04,06 |

## Key corrections vs previous skill text

Previous `sap-b1-fdd` skill said: "rounded start/end hijau" (green rounded start/end).
**WRONG.** Actual: start/end = pink/red SHARP rect. Green virtually absent (756px across entire flowchart 01 = noise).

Previous skill said: "Calibri dari /mnt/c/Windows/Fonts/calibri.ttf".
**WRONG.** Calibri = variable font, matplotlib render nondeterministik. Skill's own pitfall section contradicts this. Use DejaVu Sans.

## Shape verification

### Diamond (decision node) — confirmed triangular profile
Yellow blob 1 in flowchart 01: y=402-530, x=425-797
- Width at 10% height: 80px
- Width at 25% height: 192px
- Width at 50% height: 361px (max)
- Width at 75% height: 193px
- Width at 90% height: 86px
→ Narrow at extremes, max at middle = diamond shape confirmed

### Sharp corners — confirmed
Blue blob at (408,172)-(813,247): corner pixel filled at all 4 corners (TL/TR/BL/BR).
15px diagonal scan: all filled = sharp rect, not rounded.

## Layout

- Background: pure white `#ffffff`
- Layout: vertical, top-to-bottom
- Node width: ~400-430px @ native resolution
- Node height: ~68-76px @ native resolution
- Vertical gap between nodes: ~45px
- Arrows: solid, stroke `#4060c0` (blue) or `#303030` (dark gray)
- Arrow labels: yes/no or condition text

## Per-flowchart statistics

| Flowchart | Size | Blue px | Yellow px | Purple px | Red px | Orange px |
|---|---|---|---|---|---|---|
| 01-alur-umum | 1221x1537 | 180k | 71k | 65k | 85k | 71k |
| 02-pengadaan | 1438x1321 | 236k | 27k | 42k | 74k | 27k |
| 03-itr | 1004x1213 | 133k | 17k | 25k | 36k | 17k |
| 04-emergency | 1004x1213 | 116k | 17k | 26k | 23k | 17k |
| 05-gagal-sync | 1226x1213 | 144k | 60k | 33k | 45k | 60k |
| 06-arsitektur | 1438x890 | 51k | 0 | 103k | 68k | 0 |

Flowchart 06 (arsitektur integrasi) has no yellow/orange = no decision nodes, only process + SAP result + start/end.

## Note on `sap-b1-fdd` skill

Skill `sap-b1-fdd` is user-owned (not curator-managed). Cannot patch autonomously.
Recommended action: `hermes curator adopt sap-b1-fdd` then patch the Flowchart generator section with:
1. Replace "rounded start/end hijau" → "start/end pink sharp rect, stroke red"
2. Replace Calibri reference → DejaVu Sans
3. Add orange node type to table
4. Add corner sharpness note
5. Point to this reference file for verified spec
