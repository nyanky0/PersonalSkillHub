---
name: diagram-pixel-analysis
description: "Reverse-engineer diagram style via pixels, no vision needed."
version: 1.0.0
---

# Diagram Pixel Analysis

When `vision_analyze` / `browser_vision` is down (502 from backend), reverse-engineer a diagram's visual style programmatically via PIL + numpy pixel analysis. No vision model, no API key needed.

## When to use

- Vision model backend returns 502 or timeout
- Need to verify generated diagram matches a reference style
- Need to extract color palette, node shapes, corner style from existing diagram PNG
- Debug matplotlib/graphviz output that "doesn't look right" but can't visually inspect

## Workflow

1. `PIL.Image.open(path).convert("RGB")` → `numpy.array(img)`
2. Quantize pixels, `Counter` top colors → identify fill palette + stroke palette
3. Per color: `np.all(np.abs(arr - ref_color) < tol, axis=2)` with tol=20 → binary mask
4. BFS connected components on mask (scan every 2-3px for speed) → bbox per blob
5. Per blob: aspect ratio = width/height → classify shape:
   - aspect > 1.5 → wide rect (process node)
   - aspect 0.6-1.5 → square-ish (could be diamond at mid-height)
   - aspect < 0.6 → tall rect
6. Diamond detection: for each blob, measure width at 10%/25%/50%/75%/90% of height:
   - Diamond profile: narrow→wide→narrow (triangular)
   - Rect profile: roughly constant width
7. Corner sharpness: sample pixel at corner vs 5px diagonal in:
   - Filled at corner = sharp rect
   - Empty at corner, filled 5px in = rounded rect
8. Arrow detection: look for dark pixels in vertical gaps between blobs
   - Gap region between two nodes: `arr[y0_gap:y1_gap]`
   - Dark pixels = arrows/strokes connecting nodes

## Color extraction template

```python
from PIL import Image
import numpy as np
from collections import Counter

img = Image.open(path).convert("RGB")
arr = np.array(img)
pixels = arr.reshape(-1, 3)
q = (pixels // 16) * 16  # quantize to 16-level
top = Counter([tuple(c) for c in q]).most_common(30)
# First = background (usually white #f0f0f0), rest = fills + strokes
```

## Shape classification template

```python
# BFS connected components for a specific color
mask = np.all(np.abs(arr - np.array([r, g, b])) < 20, axis=2)
visited = np.zeros_like(mask, dtype=bool)
blobs = []

for y in range(0, H, 2):
    for x in range(0, W, 2):
        if mask[y, x] and not visited[y, x]:
            stack = [(y, x)]
            pixels = []
            while stack and len(pixels) < 50000:
                cy, cx = stack.pop()
                if cy < 0 or cy >= H or cx < 0 or cx >= W: continue
                if visited[cy, cx] or not mask[cy, cx]: continue
                visited[cy, cx] = True
                pixels.append((cy, cx))
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = cy+dy, cx+dx
                    if 0 <= ny < H and 0 <= nx < W and not visited[ny, nx] and mask[ny, nx]:
                        stack.append((ny, nx))
            if len(pixels) > 200:
                ys = [p[0] for p in pixels]
                xs = [p[1] for p in pixels]
                blobs.append((min(xs), min(ys), max(xs), max(ys), len(pixels)))
```

## Diamond detection template

```python
ys, xs = np.where(mask)
for blob_y_range:
    for frac in [0.1, 0.25, 0.5, 0.75, 0.9]:
        y_test = int(y_min + frac * (y_max - y_min))
        x_at_y = xs[ys == y_test]
        width = x_at_y.max() - x_at_y.min()
        # diamond: width narrow at extremes, max at 0.5
```

## Palette comparison as diagnosis (layout vs color)

When a user says a generated diagram "still looks bad/ugly" and a reference style exists, do NOT re-color blindly. Sample the reference fills precisely and compare hex against the current palette FIRST:

```python
from PIL import Image
from collections import Counter

def region_mode(f, x0, y0, x1, y1):
    """Dominant exact fill color in a node region of reference PNG."""
    im = Image.open(f).convert('RGB')
    px = [p for p in im.crop((x0, y0, x1, y1)).getdata() if p != (255, 255, 255)]
    return Counter(px).most_common(3)  # (color, count) tuples
```

Pick regions inside several node fills (blue process, yellow decision, purple staging, red reject). Compare to own palette.

- Colors match reference → problem is LAYOUT (crossing/missing arrows, node overlap, branch routing), not color. Do not touch palette; rebuild geometry.
- Colors differ → then re-palette.

Session case: generated flowchart palette was byte-identical to the Soltius v2.0 reference (both #DCE9F7-family pastels) yet user judged it ugly — root cause was entirely layout: boxes stacked with NO arrows between them, then misrouted branch lines crossing the main column.

## Pitfalls

- `scipy.ndimage` may not be installed — use pure BFS with numpy arrays instead
- Variable fonts (Calibri, Inter) render nondeterministically in matplotlib — verify text is visible by checking text-band height: `dark_pixels_in_text_row > 10px @ dpi140` = OK, `< 10px` = broken render
- Background color is usually the top hit in Counter but verify by checking corner pixels: `arr[0,0]`, `arr[0,W-1]`, etc.
- Multi-color fills that are close in RGB space (e.g., yellow #f0f0c0 vs orange #f0e0c0) need tol ≤ 20 to separate

## References

- `references/sap-b1-fdd-flowchart-spec.md` — verified color/shape spec for Soltius FDD flowcharts (6 reference PNGs analyzed)
- `references/flowchart-layout-engineering.md` — matplotlib geometry rules for branching flowcharts (own-column-per-side-box, L-shaped branches, y-counter-first, arrow-presence guard, semantic trace QA)
- `references/html-png-mockup-rendering.md` — chrome headless mockup PNG rendering: per-page window height, content-fill rule (empty bottom band reads as "messy"), emoji/UTF-8 pitfalls
