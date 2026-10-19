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

## Installing third-party MCP servers in Antigravity

Treat Antigravity IDE and Antigravity 2.0 / `agy` as separate hosts, even though both use Gemini branding; each has separate MCP configuration and capabilities. Identify the actual executable/UI the user means before touching config: Antigravity IDE reads the IDE MCP config; Antigravity 2.0 may be the standalone `agy` application and CLI, with its own global MCP registry/config. Follow the integration's current host-specific setup and verify available commands rather than assuming either product name implies the CLI.

On Windows, prefer `cmd.exe` with args `["/c", "npx", "-y", "<package>@latest"]` for npm MCP servers; verify the complete command independently before adding it. Do not put shell flags or package arguments into an unquoted positional name in Hermes CLI: its `--args` consumes following tokens, so either call `hermes mcp add <name> --command cmd.exe --args /c npx -y <package>` with package name kept intact, or use the verified Hermes config CLI/schema if argument parsing fails. Preserve existing entries when merging JSON/config files.

For **Antigravity IDE**, confirm the active build's MCP path from its local `mcp_servers.md` documentation rather than relying on stale web guidance; this installation's builtin docs identify `~/.gemini/config/mcp_config.json`. Do not assume `~/.gemini/antigravity/mcp_config.json` is authoritative merely because a repository example names it; check the app's docs and existing active config.

For **Antigravity 2.0 / agy**, inspect `agy mcp --help` and `agy plugin --help`; use the integration's official plugin when it provides host-specific hooks/rules/MCP, otherwise register MCP via `agy mcp add`. Check `agy mcp list` after install and avoid duplicates if a plugin already registered the same server. Restart the relevant host after configuration.

Verify each surface in its own context: use `hermes mcp test <name>` only for Hermes; use `agy mcp list` and `context-mode doctor` for CLI registration/health, then actually run an `agy` session tool prompt; inspect the IDE's MCP Servers panel or run a live IDE prompt for IDE discovery. A config file, plugin import, doctor PASS, or a successful different-host test does not prove the target host loaded tools. Report any authentication/account gate as an explicit unverified blocker, not as install failure or success.

When the IDE does not show an MCP server, first compare the file edited with the IDE's own `mcp_servers.md` (and use builtin docs on disk if available); config locations differ between IDE and CLI and can change across versions. Keep routing guidance in the host-supported instruction file; if the IDE has no hooks, disclose that enforcement is instruction-based, not programmatic.

## Pitfalls
- If a third-party MCP is absent, compare the edited path against the installed Antigravity IDE builtin `mcp_servers.md` before changing settings; IDE config locations differ from `agy` CLI paths and can vary by build.
- Skip guessing whether ACP is installed — run `hermes acp --check`.
- If the ACP agent won't show in the editor, confirm `hermes` is on the editor's
  PATH and the command/args config matches `["hermes","acp"]`.

See `references/antigravity-acp-setup.md` for the session's findings.
