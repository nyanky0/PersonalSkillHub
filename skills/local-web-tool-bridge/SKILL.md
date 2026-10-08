---
name: local-web-tool-bridge
description: "Bridge a browser web tool to a local CLI agent/process."
version: 1.0.0
platforms: [linux, macos, windows, wsl]
triggers:
  - browser tool needs to run a CLI or process
  - web tool to hermes handoff or auto-run
  - localhost companion server for a static HTML tool
  - single-file HTML tool that calls out
  - terintegrasi ke hermes dari web
---

# Local Web Tool -> CLI Bridge

A browser-side tool (single-file HTML generator, prompt studio, dashboard) CANNOT
directly spawn a CLI (`hermes chat`, a shell script) or write arbitrary files — the
browser sandbox blocks subprocess access and filesystem writes. The bridge is a
tiny **stdlib-only Python companion server** that (a) serves the HTML, (b) exposes
one POST endpoint, (c) writes artifacts to a project folder, and (d) optionally
spawns the CLI.

## Core architecture (zero dependencies)

`ThreadingHTTPServer` + `BaseHTTPRequestHandler`. One file. Endpoints:

- `GET /` — serve the tool's HTML (and `/run?name=X` for a live progress page).
- `GET /open?name=X` — reveal the outbox folder in the OS file manager (see below).
- `POST /send` — accept JSON `{name, files:{...}, auto_run:bool}`; write files into
  `~/<outbox>/<slug-name>/`; optionally spawn the CLI; return `{ok, dir, written,
  started, pid, already, hermes_available}`.
- CORS headers on every response (`Access-Control-Allow-Origin: *`, `-Allow-Headers`,
  `-Allow-Methods`) or the browser `fetch` will silently refuse the cross-origin call.
  `do_OPTIONS` returns 204.

## The 6 pieces that make it actually work (each bit someone)

1. **Serve + POST + CORS** — see above. Test `curl -s -o /dev/null -w "%{http_code}"
   http://localhost:PORT/` before touching the endpoint.

2. **Write files with PRESERVED case.** `AGENTS.md`/`PRD.md`/`SKILL.md` are case-
   sensitive for agents (Hermes reads `AGENTS.md`). Don't `.lower` the filename —
   validate against an `ALLOWED` set of lowercase names (`prd.md`, `agents.md`, …)
   but write the caller's exact `fname` so case survives.

3. **Spawn via `subprocess.Popen(cmd, shell=True, cwd=str(proj), ...)`.** The
   `cwd=proj` matters: it's what lets the agent pick up the folder's `AGENTS.md`
   automatically. Build a self-contained prompt string for the `-q` one-shot mode
   (e.g. "Baca PRD.md, AGENTS.md, tasks.md di folder ini, implementasikan MVP…").

4. **PID-file guard against double-spawn.** Every "Kirim" click re-POSTs /send. Write
   `proj/.run.pid` with `pobj.pid`; on the next call, read it and check
   `Path('/proc/'+pid).exists`. If still alive, set `already=True` and DON'T spawn
   again — otherwise you pile up orphaned agents (hit 2 stuck hermes procs this way).
   **Zombie trap**: a dead `sh` wrapper stays in `/proc` with state `Z`, so
   `/proc/<pid>.exists()` returns True forever → `already=True` → agent silently
   NEVER spawns again ("diem aja" — the #1 "why is it stuck" report). Read the state
   instead: `open(f"/proc/{pid}/stat").read().split()[2] != "Z"`. Helper:
   `_alive(pidfile)` — returns False for missing/invalid/zombie. Use it in EVERY
   handler that reads the pid file (`/run`, `/log`, `/send`), not just one.

5. **Redirect stdout to `run.log`, NOT `subprocess.DEVNULL`.** DEVNULL makes the
   background agent's work invisible — the #1 UX complaint ("agent dijalankan tapi
   gak keliatan apa-apa"). Open `run.log` and pass it as `stdout=lf,
   stderr=subprocess.STDOUT`. Log a start line first.
   **Per-run log**: open with `'w'`, NOT `'a'` — a dev folder keeps its `run.log`
   across re-sends, so append mode silently merges every new dev into one growing
   blob (349KB of mixed sessions). Fresh `'w'` per spawn = each dev gets its own
   clean log. The progress page just reads the file, so it stays correct either way.

6. **Progress page via `<meta http-equiv=\"refresh\" content=\"2\">` + server-side render.**
   Do NOT generate a live-updating page with inline JS built as nested
   Python strings — the `\"`/`\\\"` escaping converges into a syntax-error tar pit
   (it did, repeatedly). Render `<pre>` with the log text server-side and let the
   meta-refresh re-fetch every 2s. Zero JS, zero escaping pain. Show a dot/status
   from `running` (read from `.run.pid` + `/proc`).

7. **`GET /open?name=X` — open the outbox folder in the OS file manager.** Saves
   the user from hunting `~/outbox/<name>` in a terminal. Use `os.startfile(dir)`
   on Windows, `subprocess.Popen(["open", dir])` on macOS, `xdg-open` on Linux;
   return `{ok, dir}` or `404 {ok:false, error}` when the folder doesn't exist.
   Browser-side button: `fetch(BRIDGE_URL + '/open?name=' + encodeURIComponent(name))`.
   WSL caveat: the Python server lives in WSL, so `os.startfile` won't fire unless
   the server runs under native Windows Python — otherwise the explorer needs the
   `\\wsl$` path. Either run the bridge on the Windows side or accept the link as
   "open the folder" hint, not a hard guarantee.

## Show the progress link in EVERY status branch

The browser tool's send handler must build `runUrl = BRIDGE_URL + '/run?name=' +
encodeURIComponent(name)` and append it to the status message unconditionally —
NOT only in the `started` branch. If you gate it, users hit the "already running"
or "auto-run off" branch and see no link ("gada link kocak"). Put the link first,
then append a one-line note per state (started / already / hermes-missing / off).

## Empty-parens authoring (cross-cutting — applies to ANY Python/JS written this way)

Writing `` (empty parens) through `write_file`/`patch`/`execute_code` can repeatedly
drop them: `apply` → `apply;`, `def main` → `def main:`, `(function ` becomes `(function {`,
`.read` → `.read`. It's still often *syntactically valid-looking* so the error is a
misplaced `SyntaxError: '(' was never closed` far from where you think. Reliable fix:
author a small fixer `.py` to /tmp via `write_file`, build blank parens as
`chr(40)+chr(41)`, run it against the target, then verify with `python3 -m
py_compile` / `node --check` **plus a real `curl` of the endpoint**. A file that
compiles can still be a defined-but-not-invoked function (see note below). For text
that must contain literal parens, a sentinel like `__P__` then `.replace('__P__',
chr(40)+chr(41))` sidesteps the stripping entirely.

## Verification checklist

- `curl -s -o /dev/null -w "%{http_code}" http://localhost:PORT/` → 200
- When a spawned agent runs long: diagnose with `references/slow-agent-diagnosis.md` (log-volume + loop-signature grep + scope-creep check; three-layer fix: max-turns, safe-code-authoring skill preload, stack-scope in generator prompts).
- `curl -s -X POST .../send -H 'Content-Type: application/json' -d '{...auto_run:false}'` → `ok:true`, files on disk
- POST again → `already:true`, no new proc
- `curl -s ".../run?name=X"` → HTML with the log text and running status
- `curl -s ".../open?name=X"` → `{ok:true, dir:...}`; nonexistent name → `404 {ok:false}`
- Python: `python3 -m py_compile server.py`; any inline JS: `node --check` on the extracted `<script>`
- Packaging for hand-off: Python `zipfile` (never `zip` CLI — often absent on WSL)

## Self-contained user-facing extras (small, high-value, keep in the SAME single-file HTML)

This session added five features to the PRD Studio UI — all plain JS/localStorage, no
server changes beyond `/open`. Keep these in the single HTML so the tool stays one file:

1. **Auto-save results to local history** — after each successful generate, write the
   result to `localStorage` history (cap ~30 entries) so a forgotten "Save" click never
   loses work. Implement as a `pushHistory(out)` helper; call it from the generate path
   (gated by an `optAutoSave` setting), from the manual save button, and from import.
2. **Default the auto-run toggle ON** — the "spawn the agent after send" checkbox should
   default to checked (`optAutoRun: true`). Users expect generate → send → execute; a
   default-off toggle silently produces "files saved but no agent ran".
3. **"Open output folder" button** — wired to the `/open` endpoint (see piece 7).
4. **Export/Import project as JSON** — one button downloads `{name, model, files:{...}}`
   as `<name>.prdstudio.json`; the import button reads the file back, restores
   `LAST_RESULT`, re-renders, and pushes to history. Gives cheap backup + machine-to-
   machine hand-off without any server work.
5. **Token-estimate button** — before generate, estimate API cost: count calls
   (3 base + 1 if SKILL.md checked), estimate input (~1500 + prompt chars/4) and output
   (~4000/call) tokens, show "≈ N K token" in the status line. It's an estimate, not a
   bill — label it as such.

## Verify a spawned agent finished (and didn't just hit its budget)

- `tail run.log` → look for the marker `⚠ Iteration budget reached (60/60) — response may be incomplete`. The agent STOPPED at `--max-turns`, possibly before its own verification pass (browser check, broken-image check per AGENTS.md). Deliverable may be done but UNVERIFIED — run the verification yourself before reporting success.
- Session footer `Resume this session with: hermes --resume <session-id>` — surface it so the user can continue the run.

## Verifying images in the delivered page (headless browser trap)

A static page's `loading="lazy"` images BELOW the viewport never fetch in a headless browser → `naturalWidth === 0` → false "broken image" verdict (all 5/5 "broken", page actually fine). Force-load before judging:

```js
[...document.images].forEach((i, idx) => {
  i.loading = 'eager';
  i.src = i.getAttribute('src') + (i.getAttribute('src').includes('?') ? '&' : '?') + 'r=' + idx + '&t=' + Date.now();
});
// wait ~5-6s, then check naturalWidth > 0
```

Cross-check from the host: `curl -s -o /dev/null -w "%{http_code}" <url>` → 200 + bytes = HTML fine, browser verdict was an artifact.

## Related

- Hermes-side token savings for the spawned agent / long sessions:
  `references/hermes-token-savings.md` (proactive_prune_tokens, idle compaction,
  max_turns, context_length — the knobs that stop the bridge-spawned agent from
  burning tokens on stale tool output; applies to any custom-provider setup).

## Pitfalls

- **Zombie pid-guard** (`/proc/<pid>` exists but state `Z`) → `already=True` forever, agent never spawns, run.log frozen at the start line. Read `/proc/<pid>/stat` state, not mere existence (see piece 4).
- **Options after query** (`-q --max-turns N "q"`) → `error: argument -q/--query: expected one argument`, no spawn (see "Bound the auto-spawned agent").
- **Append-mode run.log** → every re-send merges into one growing log; use `'w'` per spawn (see piece 5).
- **Gated link** (show link only when started) → user never sees it on re-send.
- **DEVNULL stdout** → correctly-spawned agent that LOOKS like nothing happened.
- **No pid-guard** → one orphaned agent per click.
- **`.items`/`.read`/`.resolve`/`.home` without parens** → `'builtin_function_or_method' object has no attribute '...'` at runtime (not import time).
- **A `def` moved BELOW `if __name__ == "__main__": main`** where `main` triggers `serve_forever` — the function is never defined before the server thread needs it. Keep helper defs at module top, above the server boot.
- **`<script src=...>` body is ignored** — inserting JS by replacing the FIRST `</script>` lands it inside the CDN `<script src>` tag where it never runs (same trap as the frontend sibling skill).
- **Bridge URL when opened via `file://`** — a static HTML tool opened by double-click (`file://`) can't reach the server with a relative/origin URL. Standard fix: `const BRIDGE_URL = (location.protocol === 'file:' ? 'http://localhost:8678' : location.origin);`. Symptom when missing/left relative: "Kirim ke Hermes" silently no-ops (fetch rejects on `file://` origin), user thinks the bridge is broken. Verify by checking the HTML source for `BRIDGE_URL` before debugging the server.
- **`zip` CLI often absent on WSL** — don't shell out to `zip` for packaging; use Python's `zipfile` (`zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)`), which is always present with the interpreter. Exclude `__pycache__` by listing files explicitly.
- **WM/branding mark in the served HTML** — a personal tool handed to the user (or shared as a zip) gets a small fixed-position watermark (`position:fixed; right/bottom; opacity:.4; pointer-events:none; user-select:none`) in the bottom-right corner, e.g. `Maul`. Do it at build time so the packaged zip already carries it.

### Bound the auto-spawned agent (turn cap + scoped prompt)

The `auto_run` spawn defaults to "implementasikan MVP" with NO bound, and a coding
agent will happily run 40+ minutes — worse, if it inherits the empty-paren stripping
behavior it loops fixing the same `$x->any` breakage repeatedly and never converges.
Two mitigations:

- **Scope the `-q` prompt to ONE deliverable**, not the whole MVP: "bikin satu fitur X
  dulu" or "membuat landing page statis" beats "implementasikan seluruh MVP". The agent
  finished a full Laravel scaffold with scope wide enough to fill the void.
- **Cap turns**: pass `--max-turns N` (Hermes `hermes chat` supports it) so a loop-prone
  agent stops at a budget instead of running until it rationalizes "done".
- **Preload the paren-strip counter-skill**: add `--skills safe-code-authoring` to the
  spawn. The agent then starts with the sentinel/repair tactics instead of discovering
  the bug after 20 minutes of fix-looping. Replaces a `<hermes> --load` trick that
  silently failed. Make the cap tunable without editing code:
  `MAX_TURNS = int(os.environ.get("PRD_STUDIO_MAX_TURNS", "60"))` and interpolate it
  into the command — deployed this way in prd-studio-server.py.
- **Argument order — options AFTER the positional query.** Build the spawn as
  `hermes chat -q "QUERY" --max-turns N --skills safe-code-authoring` — the `-q`/`-s`/
  `--max-turns` options MUST follow the query string. Writing `-q --max-turns N
  --skills X "QUERY"` makes argparse treat the string as a positional → fatal
  `hermes chat: error: argument -q/--query: expected one argument`, the agent never
  spawns, and the run.log shows only the usage error (diagnostic fingerprint).
  Reproduce with `hermes chat -q --max-turns 3 "x"` (fails) vs `hermes chat -q "x"
  --max-turns 3` (runs).
- **Constrain stack choice at GENERATE time, not just execution time.** A PRD that says
  "landing page" will happily get implemented as Next.js + Supabase + 3D (the agent's
  default is over-engineering). The durable fix is in the prompt templates that BUILD the
  PRD/AGENTS files: add an explicit rule — "pilih tech stack SECUKUPNYA; landing page /
  website statis = single-file HTML+CSS+vanilla JS, tanpa framework, tanpa build step,
  tanpa npm install, tanpa backend". If the generator is an LLM prompt, embed it in the
  system/user prompt; if it's a template, add it to the template. Execution-time scope
  rules help, but the stack is chosen at generation time.

Also: the agent may scaffold into a **different directory than `cwd`** (it ran `laravel new`
into `/mnt/c/laragon/www/KopiKita` instead of `~/prd-outbox/test`). That's usually fine and
even desirable (matches the user's Laragon convention), but don't assume `find` on the outbox
folder will show the real code — grep the `run.log` for absolute paths to locate where the
agent actually worked.