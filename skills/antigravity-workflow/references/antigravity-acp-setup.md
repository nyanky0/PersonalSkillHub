# Antigravity ACP Setup — session findings

Verified 2026-08-18 on this machine (Windows, Hermes profile default).

## What was verified live

- `hermes acp --check` → "Hermes ACP check OK" — the ACP extra was already
  installed in this profile (`~/.hermes/hermes-agent/venv`).
- `hermes` resolves to `C:\Users\yudah\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes`
  so the ACP client can spawn it directly.
- VS Code Marketplace extension **ACP Client** (publisher `formulahendry`,
  id `acp-client`, v0.2.0) confirmed to exist via the marketplace gallery API.
  Note: the human-facing item URL
  `https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client`
  returns HTTP 404 to HEAD/GET requests from curl (the page is a JS app served
  with a 404 status) — do not treat that as the extension being missing; use
  the gallery API for verification:
  `POST https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery`
  with body `{"filters":[{"criteria":[{"filterType":7,"value":"<publisher>.<name>"}]}],"flags":103}`.

## ACP launcher surface (from `hermes acp --help`)

- `hermes acp` — start the server (stdout = JSON-RPC, logs to stderr)
- `hermes acp --version` / `--check` — non-interactive health checks
- `hermes acp --setup` — interactive provider/model setup for ACP terminal auth
- `hermes acp --setup-browser [--yes]` — installs agent-browser + Playwright
  Chromium (~400 MB) into `~/.hermes/node/` for browser tools; idempotent

## Docs source of truth

- User guide: website/docs/user-guide/features/acp.md in the hermes-agent repo
  (ACP Host Integration — VS Code, Zed, JetBrains, Buzz setup)
- Internals: website/docs/developer-guide/acp-internals.md
- The `antigravity-cli` operator skill ships as an OPTIONAL skill in the repo:
  `optional-skills/autonomous-ai-agents/antigravity-cli/SKILL.md` — it is NOT
  installed by default; install it before relying on agy delegation patterns.

## Key ACP facts worth remembering

- ACP sessions use the shared `~/.hermes/state.db`, are searchable via
  session_search, and survive server restarts.
- Approval options: allow_once / allow_session (per-session, resets on restart)
  / allow_always (permanent allowlist entry). On timeout or bridge error the
  approval is DENIED by default.
- ACP binds the editor's cwd to the session, so file/terminal tools run
  relative to the open workspace.
- ACP toolset (`hermes-acp`) excludes messaging delivery and cronjob management
  by design; includes file, terminal, web/browser, memory, todo, skills,
  execute_code, delegate_task, vision.
