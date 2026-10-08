---
name: safe-code-authoring
description: "Use when writing code via agent tools; empty parens strip."
---

# Safe Code Authoring (through Hermes tools)

When producing source code (JS, Python, HTML) through the agent toolchain — `patch`, `write_file`, `execute_code`, or `browser_console` expressions — a recurring failure is **literal empty parentheses `` and empty braces `{}` being dropped from the generated text**: `function f` → `function f{`, `.read` → `.read`, `def main:` → `def main:`, `testApi` → `testApi`, arrows lose `` params.

This one bug can cost dozens of fix cycles. Detect it early and switch tactics immediately.

## The tell (diagnose before looping)
- `py_compile` / `node --check` reports `expected '('`, `'(' was never closed`, or `Unexpected token '{'`.
- A diff shows a method/call missing its parens (`.read`, `.lower`, `.resolve`, `.items`, `def main:`).
- The same patch fails twice with an identical "old/new identical" or apply error.

## Workarounds (in order of reliability)
1. **Sentinel + replace** — write `__P__` wherever empty parens belong, then run a tiny script that swaps `__P__` → `chr(40)+chr(41)`. The sentinel is NOT a paren so it survives generation; the replacement script injects the real chars.
2. **Standalone repair script via `write_file`, then run it** — `write_file` of a fix `.py` proved reliable for full byte-for-byte content even when inline patches mangled parens. Prefer this over repeated inline patches.
3. **One-shot inline fix** — `python3 -c "import pathlib; d=pathlib.Path('f').read_text; d=d.replace('BAD', 'GOOD'+chr(40)+chr(41)); pathlib.Path('f').write_text(d)"`. For `.items`/`.lower`-style method calls, append `chr(40)+chr(41)`.

## Discipline that prevents the waste
- **Verify syntax every single time before running** — `node --check <extracted.js>` for JS, `python3 -m py_compile <file>` for Python. Extract inline `<script>` blocks with a regex into a temp file first (write the extractor to disk, don't inline it — `open(...).read` itself can lose parens).
- **Re-read current bytes (`read_file`) before every patch** — patching against a stale view corrupts silently. The "partial view / modified since read" warning means STOP and re-read. Use `Path.read_text` (no paren risk) not the terminal `cat`.
- **Two-strikes rule (user-mandated)** — if the SAME edit fails twice, do NOT retry inline; switch to a write_file repair script. This session the user explicitly flagged the foot-dragging: "kenapa lu lakuin tugas tadi lama banget".
- **`browser_console` expressions** — avoid IIFE `(function{...})` and arrow functions (parens strip). Use `Array.prototype.map.call(document.querySelectorAll(...), function(x){...})` or flat `'a=' + x` string concatenation. Probe remote APIs with `curl` from terminal, NOT `fetch` from the console.
- **Function ordering in Python** — keep helper `def` (e.g. `slug`, `html_escape`) ABOVE the `if __name__ == "__main__":` block that runs `serve_forever`; a helper defined below a blocking call is never defined when a request arrives (`NameError: name 'slug' is not defined`).

## Refining a stubborn edit
Stop patching the whole block; `read_file` the exact broken line, then fix only that line via a sentinel script. When a full-file rewrite keeps breaking, switch approach entirely — write the file with `__P__` sentinels, then one `replace('__P__', chr(40)+chr(41))` pass over the whole file.

## Also relevant when wiring LLM-backed tools
- A `<datalist>` is native autocomplete and looks empty until populated — for an obvious picker use a real `<select>` and fill its `<option>`s.
- When spawning long background jobs (e.g. `hermes chat -q`), redirect stdout to a `run.log` file, save the PID, and guard against double-spawn — don't sink output to DEVNULL, or the user sees "it ran" with no trace of what happened.