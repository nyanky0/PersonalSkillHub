# Flowchart Layout Engineering — matplotlib geometry rules

Learned rebuilding IBT FDD flowcharts v4 (2026-09). User judged earlier charts
"masih jelek" after several rounds of auto-layout. Root causes were layout, not
palette (palette matched the Soltius reference exactly).

## Detection: stacked nodes with NO arrows

A previous generator class auto-"connected" nodes but the arrows silently never
rendered (helper signature mismatch) — output looked like boxes piled in a
column, and vision QA misread it as a valid sequence. The ONLY reliable check is
a crop-and-zoom visual (vision_analyze on a 2x upscaled crop of the region,
asking to trace each line to its arrowhead) — never trust global "looks fine".

## Vertical single-column flow with branches — geometry rules

Reference style (Soltius v2.0 flat flowcharts): main column at CX, diamond
decisions with Yes/No branch labels, side outcomes (auto-approve, rejected)
routed LEFT or RIGHT of the column, loops back to a lower/earlier node.

Rules that ended the iteration loop:

1. Assign each side element its OWN x column — never share x between a
   side-box and the vertical run it bypasses:
   - auto-approve column x_A (far right)
   - reject/return box x_R (left of main, or far left)
   - loop-back x_L (outermost)
   Distinct columns = lines can never cross the boxes they pass.
2. Draw side branches as L-shaped polylines: horizontal from decision side
   (decision x + half-width) to side column, then vertical. No diagonals.
3. Compute ALL y coordinates from a single running counter first (y -= gap),
   THEN place side boxes relative to those y's (e.g. reject box aligned with
   the decision that rejects it). Avoids overlap by construction.
4. Recheck after EVERY render with vision on the actual PNG — loop until the
   vision pass reports no line/box crossing. Expect 3-6 geometry iterations;
   that is normal for a branching chart, not a failure signal.
5. Zoomed crop for ambiguity: when vision hedges ("line goes toward X?"), crop
   the region at 2x with PIL and re-ask vision to trace the single line to its
   arrowhead. Cheap and decisive.

## When vision says OK but logic is wrong

"Looks clean" ≠ semantically right. Walk each decision's Yes/No branch against
the documented state machine. Session bug: decision "next stage?" — the NO path
(should reach "Approved") was visually routed into the red Rejected box; a clean
layout had silently wired the wrong target. QA must trace line → endpoint, then
verify endpoint matches the intended state, not just that lines don't cross.

## Arrow rendering: verify presence before polishing

matplotlib `annotate` arrows silently no-op on signature mismatch
(`arrow() missing 1 required positional argument: 'y2'`). Guard: after first
render, zoom a mid-flow region and confirm arrowheads exist between adjacent
nodes. If missing, the whole chart needs a re-render pass, not label tweaks.
