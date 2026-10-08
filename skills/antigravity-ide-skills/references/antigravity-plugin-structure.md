# Antigravity plugin bundle structure

Full plugin packaging (beyond flat skills). Staged by CLI/IDE into global config:
`~/.gemini/antigravity-cli/plugins/<plugin>/` (CLI) or `C:\Users\<user>\.gemini\config\plugins\<plugin>\` (IDE).

## Layout
```
plugin.json                 # Required manifest
mcp_config.json             # Optional MCP servers
hooks.json                  # Optional pre/post tool event hooks
skills/                     # Optional specialized skills
agents/                     # Optional subagent defs
rules/                      # Optional codebase rules
```

## plugin.json manifest
```json
{
  "$schema": "https://antigravity.google/schemas/v1/plugin.json",
  "name": "my-plugin",
  "description": "A brief description of what my plugin does."
}
```
- `name` required, pattern `^[a-zA-Z0-9-_]+$`.
- `description` optional.

## Skills (flat, no plugin) — two scopes
- Global: `~/.gemini/config/skills/<name>/SKILL.md` (or IDE equivalent `C:\Users\<user>\.gemini\config\skills\`).
- Project / workspace: `<repo>/<skills-dir>/<name>.md` — lives with git repo. Name from frontmatter becomes slash command.

## Flat SKILL.md frontmatter (used by Hermes/Claude/Antigravity)
```yaml
---
name: format-tests
description: Standardize and re-format Python unittest assertions
---
body...
```