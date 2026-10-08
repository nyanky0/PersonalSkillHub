---
name: reliable-code-file-edits
description: "Edit code files without dropped-paren syntax breakage."
---

# Reliable Code File Edits

Techniques for writing and patching code files through `write_file` / `patch` /
`execute_code` / terminal heredocs without introducing silent syntax breakage,
and for catching breakage immediately.

## The core failure mode: dropped empty parentheses

When generating code that contains **empty** call parens — `foo`, `.lower`,
`.items`, `.read`, IIFE closers `})`, arrow calls `apply` — the literal
`` can silently vanish from the generated text, producing `foo{`, `apply;`,
`.lower`, `.read`, `(function {`, `def main:`. This is a model-output quirk,
NOT a tool bug, and it recurs across write_file, patch, execute_code, inline
`python3 - <<EOF`, and browser_console expressions alike. It does not show up
in a normal syntax check of surrounding code and often only surfaces as a
`SyntaxError`/`NameError`/`TypeError` at the new line far later.

Symptoms to recognize early: `AttributeError: 'builtin_function_or_method'
object has no attribute ...` (e.g. `.read` used where `.read` was intended),
`SyntaxError: '(' was never closed`, `NameError: name 'x' is not defined` for a
function you clearly defined, or `function`/`def main`/`async function testApi`
with a missing ``.

## Workaround that works: sentinel + chr

Do NOT keep re-emitting the raw `` in the content you write — it may get
stripped again (observed repeatedly). Instead, author the file using a sentinel
token that is NOT empty parentheses, then replace it programmatically:

1. Write the file with `__P__` (or any sentinel) wherever an empty paren call
   is needed: `def slug(name): ... s = x.lower__P__.strip(...)`, `main__P__`.
2. Write a small repair script (via write_file, which carries the sentinel
   safely) that does the replacement:
   ```python
   import pathlib
   p = "/path/to/file"
   d = pathlib.Path(p).read_text(encoding="utf-8")
   C = chr(40) + chr(41)   #
   d = d.replace("__P__", C)
   pathlib.Path(p).write_text(d, encoding="utf-8")
   ```
3. Run it, then verify (below).

For one-off inline fixes, build the replacement string with `chr(40)+chr(41)`
concatenation rather than typing the literal ``.

## Verify after EVERY edit — don't assume it landed

After each write/patch to a `.py` file: `python3 -m py_compile <file>` and check
exit 0. After each `.js`/inline-`<script>` change: extract the script and
`node --check` it:

```bash
python3 -c "import re,pathlib; d=pathlib.Path('x.html').read_text(encoding='utf-8'); s=re.findall(r'<script>(.*?)</script>', d, re.S); pathlib.Path('/tmp/inline.js').write_text('\n'.join(s), encoding='utf-8')"
node --check /tmp/inline.js && echo OK
```

`py_compile` passes for some paren-loss cases (a missing `)` that's actually a
runtime bug like `.lower).strip` strips a bound-method rather than erroring at
compile time), so also grep the changed lines back and eyeball that `` are
present where a call is intended — don't trust the compile alone.

## Pitfalls

- **A missing `` is a runtime bug, not always a syntax error.** `.lower).strip`
  or `re.sub(...)` that lost its closing `)` can pass `py_compile` yet fail at
  import/run. Always run the file once (`python3 file.py`) or at least grep the
  edited region before declaring done.
- **Inline heredocs and browser_console expressions are just as affected.** If a
  `browser_console` `expression` keeps returning `SyntaxError: Unexpected token
  '{'`, it's likely the same dropped-paren problem in the expression you typed,
  not a page problem — recheck what you actually emitted.
- **`patch` old_string/new_string with empty parens** can "succeed" while still
  writing `});` instead of `})` (call paren dropped at the close of an IIFE),
  which silently leaves the IIFE DEFINED but never INVOKED — the page then has 0
  JS errors but the feature doesn't run. After patching an IIFE/slider/init
  block, confirm the trailing `})` (or ``) landed, and confirm the effect
  happened (dots appended, display set, etc.), not just that console is clean.
- When a regex-based repair `assert old in d` fails repeatedly, stop and
  `read_file` the exact current bytes — the file may already carry a mangled
  variant (e.g. a literal `'+C+'` from a prior inline concat attempt) that your
  "correct" match no longer equals. Match the actual current text, not the text
  you intended to write last time.

## Escape-hatch: don't generate JS-inside-Python-string at all

When you're building an HTML page *by concatenating strings in Python* (or any
host language) and that page also needs live-updating behavior, the nested
escaping is where the worst breakage lives: the HTML layer wants `\"`, the
JS-string layer wants `\\"`, and empty-paren drops add a third failure axis.
You end up with lines like
`html.append("if(x){a=b||\"literal\";}")` and the `\"`/`\\` go wrong in ways far
harder to eyeball than a plain missing ``.

**Simplest fix: render server-side and skip the client JS entirely.**
For any "show me what a background job is doing" page, emit the current
state server-side (read the log file, check the pid) and add
`<meta http-equiv="refresh" content="2">` so the browser reloads it. A 2-second
meta-refresh is visually fine for a progress/log view, needs zero client
JavaScript, and sidesteps the whole escaping/paren problem. Only reach for a
`fetch` poller when you need sub-second updates or avoid a full reload.

This is what actually closed out the PRD-studio `/run` log-viewer build: three
failed attempts at a JS `setTimeout(tick)` poller (each mangled by escaping)
were replaced by one server-rendered page with meta-refresh, and it worked
first shot.