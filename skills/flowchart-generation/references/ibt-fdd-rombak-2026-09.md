# IBT FDD flowchart rombak (2026-09) — session record

User complaint: "flow chart nya berantakan banget" after FDD v1.6 was
delivered. Two root causes, both real:

1. **Stale embedded images** — docx v1.6 embedded flowcharts_v4 PNGs
   (verified: md5 image2..8 in word/media == flowcharts_v4 files) while
   v5 fixes existed. `FLOWDIR` in `fdd_common.py` still pointed at
   `flowcharts_v4`. Fix: repoint + rebuild + md5-verify.
2. **Real geometry bugs in v4/v5 generators**:
   - horizontal connector stopping at `CX+HW` (column edge) instead of the
     side-box edge → dangling arrow in empty space
   - `y1+40` = 12px below box (half-height 28) → arrowhead floating
   - returned/rejected/stage-loop lanes sharing x columns (XL=XS=160) →
     segment-segment crossings
   - side boxes at negative x (center CX-585 with w 240 → left edge -120)
     → clipped off-canvas

## v4 vs v5/v8 structural differences (what "raplh" meant)
- flat single-column chain; side boxes (reject/return/loop/bypass) each on
  own x lane, ≥120px apart; horizontal connectors only in gaps between
  lanes, verified zero-crossing
- reject exits box bottom, return exits box left — never both converging
  on one side
- elbows enter top-center of target box at x = CX+80 (inside span), not at
  a corner
- final state: 8 flowcharts, TOTAL crossing 0, nembus 0, all nodes in
  canvas (audit via save() monkeypatch)

## Docx media verification recipe
```python
import zipfile, hashlib
z = zipfile.ZipFile(docx)
for n in sorted(x for x in z.namelist() if x.startswith('word/media/')):
    print(n, hashlib.md5(z.read(n)).hexdigest()[:8])
```
Compare against `md5sum flowcharts_v5/*.png`. Any mismatch = stale embed.

## Vision reliability notes (this dataset)
- content hallucination: YES, reliably (invented chemical/agricultural
  labels, wrong companies, Vietnamese text on Indonesian diagrams)
- structural verdicts: sometimes accurate (v4 siklus critique matched
  code), sometimes fabricated (claimed crossings that audit disproved)
- rule: trust audit; use vision only as spot-check, reconcile in favor of
  deterministic tests
