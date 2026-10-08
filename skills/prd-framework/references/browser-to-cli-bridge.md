# Browser → local CLI bridge (companion server pattern)

When a single-file browser tool (HTML+JS) needs to drive a local agent CLI
(Hermes, or any `hermes chat -q ...`) or write files outside the browser sandbox,
a browser page cannot do it directly. The fix is a tiny stdlib-only Python
server that (a) serves the HTML and (b) exposes a `/send` (or similar) POST
endpoint the page calls with `fetch`.

## Why the bridge is necessary

- Browser JS cannot spawn processes or touch the filesystem outside its own
  sandbox. No `fetch('http://localhost')` changes that.
- The *real* "integration" is writing `AGENTS.md` (and `PRD.md`/`tasks.md`) into
  a project folder, then running `hermes chat` from that folder: Hermes
  auto-reads AGENTS.md as project context. The bridge is what turns a browser
  click into that on-disk handoff.

## Server shape (proven, stdlib only)

- `ThreadingHTTPServer` on `http://0.0.0.0:<port>` (pick a port, e.g. 8678).
- `do_GET` serves the HTML (and any sibling assets).
- `do_POST /send` parses JSON `{name, files, auto_run}`, slugifies `name`,
  writes each file into `<outbox>/<slug>/`, then — if `auto_run` — spawns the
  CLI via `subprocess.Popen(cmd, shell=True, cwd=proj_dir, ...)`.
- Return JSON `{ok, dir, written, started, ...}` so the page can report success.
- CORS headers (`Access-Control-Allow-Origin: *`, OPTIONS handler) let the page
  call it from the `file://` origin too (then page targets `http://localhost:<port>`,
  not `location.origin`).

## Key gotchas (all hit in one session)

1. **Whitelist + preserve filename case.** The browser sends `PRD.md`,
   `AGENTS.md`, `tasks.md`, `SKILL.md`. Do NOT `.lower` the filename — Hermes
   looks for exact-case `AGENTS.md`. Validate against a whitelist set
   (`{"prd.md","agents.md","tasks.md","skill.md"}`) case-insensitively, but
   write the ORIGINAL name. Lowercasing silently produced `agents.md` that
   Hermes wouldn't pick up.

2. **Define helper functions (like `slug`) BEFORE the server loop.** If a helper
   lands *below* the `if __name__ == "__main__": main` block, and `main` is
   the first thing that runs `serve_forever` (a blocking loop), the helper is
   never defined when a request arrives → `NameError: name 'slug' is not
   defined` at request time, not at startup. `py_compile` will still pass
   because it's a runtime reference, not a syntax error.

3. **Empty-paren mangling when writing Python through edit tools.** The author
   repeatedly emitted `` that got stripped, landing `Path.home` as `Path.home`,
   `self.end_headers` as `self.end_headers`, `main` as `main`, `def main` as
   `def main`, and `.lower.strip` losing a closing paren. Workaround that
   finally held: write a fixer `.py` to `/tmp` via `write_file`, build blank
   parens as `chr(40)+chr(41)` (never type `` literally), run it, then verify
   with `python3 -m py_compile`. Watch for the sneaky `re.sub(...)` that loses
   its final closing `)` — `py_compile` flags it but the message points at the
   `.strip(` line, not the `re.sub` line.

4. **Browser (LLM) side gotcha on the page:** guard the fetch against the
   `file://` case — `BRIDGE_URL = (location.protocol === 'file:' ? 'http://localhost:8678' : location.origin)`.
   Also disable the send button during the POST and surface a clear error when
   the bridge isn't running ("pastikan python3 X-server.py jalan").

## Spawning the agent: don't leave the user blind

The first cut spawned `hermes chat -q` with `stdout=subprocess.DEVNULL` — the
agent ran for 5–10 minutes with the user seeing only a "Hermes agent dijalankan"
toast and no way to watch progress, and every extra click spawned a *second*
agent. Three fixes make the handoff actually usable:

1. **Redirect agent output to `run.log`** in the project folder, not `/dev/null`:
   ```python
   lf = open(logf, 'a', encoding='utf-8')
   pobj = subprocess.Popen(cmd, shell=True, cwd=str(proj), stdout=lf, stderr=subprocess.STDOUT)
   ```
   This is the difference between "agent berjalan" (user sees nothing) and a
   real monitorable run. Surface the seam in the page's success message too:
   tell the user how to watch it.

2. **Anti-double-spawn guard with a pidfile.** Write `proj/.run.pid` after
   Popen, and on each `/send` check `Path('/proc/' + pid).exists`; if alive,
   return `already:true` and skip spawning. Without this, N clicks = N agents.

3. **A live log-viewer page** (`GET /run?name=<slug>`). Render the current
   `run.log` + running-status server-side and auto-refresh with
   `<meta http-equiv="refresh" content="2">` — NO client JS. (Doing it as a JS
   `setTimeout(tick)` fetch poller instead means generating JS inside Python
   string concat, where nested `\"`/`\\"` escaping collides with empty-paren
   drops and breaks repeatedly; the server-rendered meta-refresh page worked
   first shot. See `reliable-code-file-edits` skill.) The page shows a
   green/red dot for running/done and dumps the escaped log into a `<pre>`.

## Verify end-to-end (do all, don't stop at the first)

1. `GET /` → 200.
2. `POST /send` with `auto_run:false` → 200, and `ls` the outbox folder shows
   `PRD.md` / `AGENTS.md` / `tasks.md` / `SKILL.md` with CORRECT case.
3. `POST /send` with `auto_run:true` → `started:true`, then `pgrep -af hermes`
   shows the spawned process with `cwd` = the project folder.
4. Clean up the test spawn afterwards (kill the PID) so it doesn't linger.