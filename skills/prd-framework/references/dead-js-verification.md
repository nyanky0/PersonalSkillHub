# Dead code in browser tools: "0 errors" ≠ "it ran"

A clean browser console and a passing `node --check` only prove the JS *parsed*.
They do NOT prove your init code executed. The failure mode that cost the most
time across the SP IKG and PRD Studio sessions was this exact gap.

## The trap: a defined-but-never-called IIFE

An IIFE whose empty call paren was dropped — `(function { ... });` instead of
`(function { ... });` — is *syntactically valid* JS. The engine defines the
function expression and discards it. No error is thrown. The feature inside
(carousel init, progress-bar wiring, magnetic-CTA handler) silently never runs.

Fingerprint (all true at once):
- console clean, `node --check` clean,
- but the DOM is missing whatever the IIFE should have created:
  - carousel: 0 dots rendered, counter stuck at its hardcoded initial text,
    slider `style.display` still `""` although the code sets it to `"block"`,
  - the slides are stacked (all `opacity:1`, `transform:none`) because the
    positioning/apply routine never ran.

## Why `node --check` and the console lie to you

- `node --check` validates syntax, not reachability. A dead IIFE is valid syntax.
- The browser console reports *uncaught exceptions*, not *code that never ran*.
- `reveal.in`, `split-line.in` firing earlier in the same script is a red
  herring — those live in a DIFFERENT IIFE whose parens were intact. One broken
  paren only kills its own IIFE, not the whole script.

## The correct verification: assert the SIDE EFFECT, not the parse

After any JS edit, don't just check syntax or console. Query the state the code
should have mutated:

```
document.querySelectorAll('.sdot').length     // carousel dots built?
document.getElementById('slCount').textContent // counter advanced from its literal?
document.getElementById('menuSlider').style.display // == 'block', not ''
```

When the side effect is absent AND there are zero errors: suspect a
defined-but-never-called function first (dropped ``, or the function is
gated behind another dead IIFE), before suspecting anything deeper.

## Related authoring hazard

The root cause of the dropped parens was the assistant emitting empty ``
that its own output stripped. When writing code through edit tools, build empty
parens as `chr(40)+chr(41)` (or a `__P__` sentinel replaced in a follow-up
`write_file`), and always re-verify with a side-effect assertion after — see
`browser-to-cli-bridge.md` gotcha #3 for the server-side variant.