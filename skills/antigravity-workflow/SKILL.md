---
name: antigravity-workflow
description: "Use when integrating Hermes with Antigravity IDE or agy CLI."
version: 1.0.0
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [antigravity, agy, ide, acp, vscode, coding-agent]
---

# Antigravity Workflow

Connecting Hermes and Google Antigravity (a VS Code fork) in both directions for
this user's coding work. Antigravity is not listed in the default installed
skills (`antigravity-cli` lives under `optional-skills/` in the hermes-agent repo
and is NOT installed by default), so the workflows below are first-class here.

Two distinct surfaces — keep them apart:
1. **Antigravity the IDE** — a full VS Code fork. Hermes runs *inside* it.
2. **Antigravity CLI (`agy`)** — a terminal coding-agent backend. Hermes drives it.

## Direction A — Hermes inside the Antigravity IDE (ACP)

Hermes runs as an ACP (Agent Client Protocol) stdio server; Antigravity presents
it in an editor chat panel like Claude Code/Copilot.

Steps (verified on this machine: `hermes acp --check` = OK):

1. Ensure the ACP extra is installed once:
   `cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'`
2. Install the **ACP Client** extension in Antigravity:
   publisher `formulahendry`, extension id `acp-client` (on VS Code Marketplace;
   verified live). If Antigravity restricts the marketplace, download the `.vsix`
   and use Extensions > "..." > Install from VSIX.
3. Open the ACP Client panel (Activity Bar) → select **Hermes Agent** → Connect.
   If the agent doesn't appear, define it manually in settings (`acp.agents`):
   ```json
   { "acp.agents": { "Hermes Agent": { "command": "hermes", "args": ["acp"] } } }
   ```
4. ACP mode reuses the configured provider/model (`hermes model`), memory,
   skills, and a curated `hermes-acp` toolset (read/write/patch/search_files,
   terminal, web, execute_code, delegate_task). Dangerous terminal commands
   surface as editor approval prompts: Allow once / Allow for session (resets per
   session) / Allow always (permanent allowlist).

Simplest always-works fallback inside any IDE: open the built-in Terminal panel
at the workspace and run `hermes` there — full agent, cwd = workspace, minus the
nice chat/diff UI.

## Direction B — Hermes delegating to Antigravity CLI (`agy`)

To have Hermes hand coding work to Antigravity's own agent (useful when the
user is already an Antigravity user and wants a Gemini-family cross-check, or an
agy worker):

- The operator guide is the repo's optional skill
  `autonomous-ai-agents/antigravity-cli` (under
  `optional-skills/` in the hermes-agent checkout). Prompt says it's an official
  shipped skill, so install it (`hermes skills install ...` or copy) rather than
  duplicating it.
- Quick shapes: one-shot `agy -p 'prompt'` (plain-text stdout, no JSON, no
  `--max-turns` — bound with `--print-timeout`), interactive via PTY+tmux.
- Treat agy as a worker backend / third-opinion reviewer, not an orchestration
  primitive.

## Pitfalls
- Do not confuse IDE-ACP (Direction A) with the agy CLI (Direction B).
- Skip guessing whether ACP is installed — run `hermes acp --check`.
- If the ACP agent won't show in the editor, confirm `hermes` is on the editor's
  PATH and the command/args config matches `["hermes","acp"]`.

See `references/antigravity-acp-setup.md` for the session's findings.
