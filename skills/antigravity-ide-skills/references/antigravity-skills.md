# antigravity-skills

# Antigravity Skills & Customizations

Deploy SKILL.md skills to Google Antigravity IDE / Antigravity CLI. Skills auto-register as slash commands (`/name`). Format is nearly identical to Claude/Hermes SKILL.md — frontmatter `name` + `description` (both REQUIRED), then markdown instructions.

## Skill locations

| Scope | Path |
|---|---|
| Global (all projects) | `~/.gemini/config/skills/<name>/SKILL.md` |
| Project (per repo) | `<project-root>/.agents/skills/<name>/SKILL.md` |
| Builtin (read-only reference) | `~/.gemini/antigravity/builtin/skills/<name>/SKILL.md` |

Windows home: `C:\Users\<user>\.gemini\...`. The builtin `agy-customizations` skill ships the authoritative docs at `~/.gemini/antigravity/builtin/skills/agy-customizations/docs/` (skills.md, json_configs.md, plugins.md, hooks.md) — read those before guessing.

## SKILL.md format

```markdown
---
name: my-skill
description: Use when <trigger>. Third person, states what + when.
---
Instructions here. Use references/ for bulky docs, scripts/ for helpers, link relatively.
```

- Frontmatter must have `name` + `description` or the skill is skipped.
- Skill dir name should match `name`; `~`/absolute/workspace-relative paths all resolve.
- Progressive disclosure: keep SKILL.md concise, push bulk into `references/`, `scripts/`, `examples/` subdirs.

## Registering skills outside default dirs — skills.json

Global config root `~/.gemini/config/` (or project `.agents/`) accepts `skills.json` / `plugins.json` pointing at skill dirs — avoids copying skills into every project:

```json
{
  "entries": [
    { "path": "~/.gemini/config/skills", "exclude": ["hermes-.*", ".*-api"] }
  ]
}
```

Fields: `entries` (path entries) + `inherits` (other config files, merged in order). Path entry supports `include_only` / `exclude` regex on directory names. Path resolution: `/` = absolute, `~/` = home, else workspace-relative.

## Bulk-sync from Hermes skills

1. Iterate `~/.hermes/skills/**/SKILL.md`, copy to dest `skills/<name>/`.
2. Use the frontmatter `name` field for the dest dir (NOT the source folder name) — Hermes dirs are category-scoped, Antigravity wants the skill's own name.
3. Strip CRLF: `b.replace(b'\r\n', b'\n')` on every copied .md. CRLF breaks YAML frontmatter parsing AND leaks `\r` into dir names (`mkdir "name\r"`).
4. Strip UTF-8 BOM (`\xef\xbb\xbf`) from the start of every copied file — BOM before `---` makes the frontmatter regex fail to match AND triggers scanner findings (invisible_unicode) that block hub installs.
   Sync script applies `sed '1s/^\xef\xbb\xbf//'` after `tr -d '\r'`.
   Source files with BOM: detect with `xxd -l 3 file.md | grep 'efbb bf'`, fix with `python3 -c "d=open('$f','rb').read(); open('$f','wb').write(d.lstrip(b'\xef\xbb\xbf'))"`.
5. Missing frontmatter = silent skip. Skills without `---\nname:\ndescription:\n---` are ignored.
   Run frontmatter check after sync: `python3 - <<'EOF'` with regex `^---\s*\n(.*?)\n---\s*\n`
   and assert both `name:` and `description:` keys exist.

## Verification

- Structural: JSON parse `skills.json`, resolve path, count dirs, assert each has SKILL.md (do from WSL shell).
- Functional (cannot be done from WSL shell — IDE runs on Windows): restart IDE / reload window, open project, type `/` in agent chat and look for the skill, or ask the agent to list skills. Agent loads skills at session start.
- `agentapi` CLI (`.gemini/antigravity-ide/bin/agentapi.bat`) refuses without `ANTIGRAVITY_LS_ADDRESS` — only set while IDE runs; not a usable probe from a plain shell.

## Pitfalls

- **Agent refusing with a GENERIC answer (e.g. "cannot do X, consider tool Y" naming tools NOT in the skill) = skill not loaded**, not a policy refusal. Deployed after IDE session start = old session never saw it. Fix: user restarts IDE / reloads window, session reloads skills at start. Don't burn time editing skill content to dodge a policy that isn't firing.
- `ANTIGRAVITY_LS_ADDRESS` is only set inside the running IDE process — not in User/Machine env, not in WSL shell. Probe via `powershell.exe [Environment]::GetEnvironmentVariable(...)` (both scopes) before concluding agentapi is usable; usually it isn't.
- Antigravity IDE runs on Windows even when the agent is in WSL — computer_use/cua cannot capture it; verification is user-side.
- `.agents/skills.json` inside a project makes that project load skills even if global discovery is off — handy for one-off projects.
- Register projects in `~/.gemini/projects.json` as `c:\\laragon\\www\\<name>` keys (single backslash in the actual string; watch Python `\\\\` vs `\\` — json.dump double-escapes).
- Windows file organizers may auto-move files written to Downloads into subfolders — re-locate with find before declaring a write lost.
- **External GitHub skills not tracked by Hub** — skills like `lazy-dev` (from `takazudo/claude-resources`) live ONLY in `~/.gemini/config/skills/` and vanish on IDE reset/cleanup. Always note the source URL when installing non-Hub skills so future sessions can re-install. Re-install: `curl -sL <raw-url> -o ~/.gemini/config/skills/<name>/SKILL.md` (strip CRLF first).
- **IDEMemory (background curator) refuses patch without fresh content.** After `skill_view(name)` returns, the content is cached in the review context. If a prior turn failed, re-call `skill_view` to refresh before retrying `skill_manage patch`.
  - `lazy-dev` → `https://github.com/takazudo/claude-resources/blob/main/skills/lazy-dev/SKILL.md`
  - Re-install: `curl -sL <raw-url> -o ~/.gemini/config/skills/<name>/SKILL.md` (strip CRLF first)
- **IDEMemory (background curator) refuses patch without fresh content.** After `skill_view(name)` returns, the content is cached in the review context. If a prior turn failed, re-call `skill_view` to refresh before retrying `skill_manage patch`.