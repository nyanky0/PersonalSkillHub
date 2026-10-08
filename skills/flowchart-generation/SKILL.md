---
name: flowchart-generation
description: QA matplotlib flowcharts via geometry audit, not vision.
---

# Flowchart Generation & QA (matplotlib)

For FDD/process-doc flowcharts rendered via matplotlib (box/oval/decision nodes, edge-to-edge arrows). Produced for IBT FDD (v4→v5/v8 rombak, 8 flowcharts) — geometry bugs there were real and user-visible ("flowchart nya berantakan banget").

## Trust chain (source of truth, highest first)
1. **Generator code geometry** — node bounds recorded, arrows edge-to-edge from recorded bounds.
2. **Deterministic audits** — segment-vs-node ("nembus") and segment-vs-segment ("crossing") intersection tests, canvas-bounds check.
3. **md5 verification of embedded artifacts** — docx/zip `word/media/` hashes MUST match freshly generated PNGs. Stale dir pointer = user sees old images.
4. **vision_analyze STRUCTURAL questions only** ("any dangling arrow? crossing? text on box?") — it hallucinates node *content* reliably (invented chemical labels, wrong company names, foreign-language text). Never trust it for content; pointed structural Qs sometimes accurate, sometimes not — always back with audit.
5. **Pixel scans** (non-white ratio) only for page-map heuristics.

## Geometry rules (hard-won)
- Every node registered with explicit `(x, y, top, bot, left, right)` bounds; arrows computed FROM those bounds. NEVER hardcode offsets like `y1+40` relative to center — box half-height 28 means `y1+40` lands 12px below box = dangling arrow head at empty space. Use `nodes[i][1..4]` edges directly.
- FancyArrowPatch auto-shortens shaft by `mutation_scale` (default ~14) to fit arrowhead. Min segment length ≈ 2× mutation_scale or head clips/misses. Short final elbow segments (16–18px) are valid if > mutation_scale.
- Side lanes (reject/return/loop/bypass): each semantic path gets its OWN distinct x column; keep ≥120px between parallel vertical lanes. Horizontal connectors must not cross vertical lanes — check with crossing audit, do not eyeball.
- Reject/return split: reject exits box BOTTOM, return exits box LEFT (or vice versa) — same box, opposite directions, never both on one side converging.
- Canvas: keep side boxes fully inside (center_x ≥ w_box/2 + margin). Center column at CX, side lanes left of CX-… and right of CX+… — compute, don't guess.
- Diamond decision: Ya/Tidak labels adjacent to correct branch; vertical chain out of decision bottom vertex, not box edge.

## Pitfalls
- Patching Python source containing `\n` inside string literals: replacement must contain SINGLE backslash. `\\n` (double) renders literal `\n` text in the diagram. Verify with grep after patch.
- Escaped quotes in patch strings through execute_code double-escape — re-check file, not the diff.
- When regenerating assets for an existing document: update the asset-dir constant (e.g. `FLOWDIR`) in the build script BEFORE rebuild, then verify embedded md5 — otherwise doc keeps old broken images and user rightly complains.
- Multiple rewrite attempts of the same generator drift in quality; prefer targeted patches to a working bound-based generator over full rewrites.
- Crossing audit must run on the SAME code path that saves PNGs (monkeypatch `save()`), else it audits dead code.

## Workflow
1. Generate: bound-based generator, one function per flowchart, shared C class (node registry, chain(), exitL/R, enterL/R/Top).
2. Audit: monkeypatch save → collect node bounds + arrow segments → assert (a) all segments end exactly at a node edge, (b) no segment intersects a node other than source/target, (c) no segment-segment crossing, (d) all node bounds within canvas. Iterate to zero.
3. Visual spot-check via vision_analyze with STRUCTURAL question only; reconcile discrepancies in favor of audit.
4. For docx embedding: set asset dir, rebuild, `zipfile` md5 of `word/media/imageN.png` must equal generator output md5s.
5. Convert to PDF (soffice headless), `pdfinfo` page count, pdftoppm sample pages — page-map via pdftotext per page.

## Support files
- `scripts/flowchart_audit.py` — deterministic crossing/nembus/bounds audit via save() monkeypatch. Copy & point at your generator module.
- `references/ibt-fdd-rombak-2026-09.md` — full session record: root causes of "berantakan" complaint, lane-geometry fixes, docx md5 verification recipe, vision reliability notes.

## Master Corporate Draw.io Flowchart Standard (via `corporate-flowchart-architect`)
Untuk seluruh diagram alur proses bisnis resmi Soltius FDD:
- Gunakan master skill **[`corporate-flowchart-architect`](../corporate-flowchart-architect/SKILL.md)** yang berkolaborasi dengan **[`drawio-skill`](../drawio-skill/SKILL.md)**.
- Menerapkan palet Soltius Blue (`#4F88BB`), node putih bersih (`#FFFFFF;strokeColor=#000000;strokeWidth=1.5`), konektor ortogonal, dan system badges (`ADD-ON`, `HUB`, `SAP B1`).
- Mengunci penomoran integer murni (1..N), peleburan decision node, dan ketiadaan fitur fiktif (*zero-hallucination*). Matplotlib generator hanya digunakan sebagai fallback headless.

