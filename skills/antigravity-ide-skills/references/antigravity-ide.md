# antigravity-ide

# Antigravity IDE customizations (skills, plugins, paths)

Antigravity IDE (VS Code-based Google AI IDE) shares the same agent harness as
Antigravity CLI / Antigravity 2.0. Skills are the same SKILL.md format as
Claude Code / Hermes: directory with `SKILL.md` containing YAML frontmatter
(`name` + `description` required) plus optional `scripts/`, `examples/`,
`resources/`, `references/` subdirs.

## Key paths (Windows user)

- Global customization root: `C:\Users\<user>\.gemini\config\`
- Global skills dir (auto-scanned): `C:\Users\<user>\.gemini\config\skills\<skill-name>\SKILL.md`
- Global registrar file: `C:\Users\<user>\.gemini\config\skills.json`
- Project scope: `<project-root>\.agents\skills\<skill-name>\SKILL.md`
- Builtin skills + authoritative docs (read these first, they live on the machine):
  `C:\Users\<user>\.gemini\antigravity\builtin\skills\agy-customizations\docs\skills.md`
  and `docs\json_configs.md`
- Project list for bulk ops: `C:\Users\<user>\.gemini\projects.json` (Windows-style paths)
- IDE agent API: `C:\Users\<user>\.gemini\antigravity-ide\bin\agentapi.bat` (needs `ANTIGRAVITY_LS_ADDRESS` from a running IDE session; useless standalone)

## Skill scopes

1. **Global** — drop skill dirs into `config/skills/`. Applies to every project.
2. **Project** — `<project>\.agents\skills\`. Workspace-scoped; IDE discovers `.agents/` automatically.
3. **Registered via `skills.json`** — point to any shared dir, no copying needed. Best for "use all skills everywhere":
   ```json
   { "entries": [ { "path": "~/.gemini/config/skills" } ] }
   ```
   Place `skills.json` in `~/.gemini/config/` (global root) or `<project>\.agents\` (project root).
   Schema: `entries[]` (paths to scan) + `inherits[]` (other config files). Each entry supports
   `include_only` / `exclude` (regex on dir names). Path resolution: absolute `/`, home `~/`,
   else workspace-relative to repo root.
4. **Plugins** — separate system, not skills. `config/plugins/<name>/plugin.json` manifest; skills can be bundled inside a plugin under its `skills/` dir. Managed via `agy plugin` subcommands (CLI).

## Sync Hermes skills -> Antigravity (global)

Run `scripts/sync-hermes-skills.sh` (copies all `~/.hermes/skills/**/SKILL.md`, renames folder
to the frontmatter `name`, strips CRLF). Then verify frontmatter of every file: name + description
present. Format check: `re.match(r'^---\s*\n(.*?)\n---\s*\n', txt)` must pass and both keys exist.

## Pitfalls

- **CRLF kills YAML names.** Hermes skill files with CRLF line endings: `grep '^name:'` returns
  `name: foo\r`, and the destination dir becomes `foo\r` — unreadable. Always `tr -d '\r'` on copy
  (sync script does this). Detect: `ls "$DEST" | grep -P $'\r'`.
- **UTF-8 BOM kills frontmatter regex.** Files starting with `\xef\xbb\xbf` before `---` make the
  frontmatter regex fail silently — skill is skipped with no error. Sync script strips BOM via
  `sed '1s/^\xef\xbb\xbf//'` after `tr -d '\r'`. Old Hermes skills may have BOM from Windows editors;
  always re-run sync after fixing source files. Detect: `xxd -l 3 "$f" | grep 'efbb bf'`.
- **Missing frontmatter = silent skip.** Skills without `---\nname:\ndescription:\n---` are silently
  ignored by sync script and IDE scanner. Always run frontmatter check after bulk sync.
- **Folder name = frontmatter `name`, not the source dir name.** Copying `antfu-web-design-guidelines`
  whose frontmatter says `name: web-design-guidelines` yields `config/skills/web-design-guidelines/`.
  Casing preserved verbatim (`Laravel`, `Vue`, `Windows`) — correct, but check case-insensitive dupes
  after bulk copy: `ls | tr 'A-Z' 'a-z' | sort | uniq -d`.
- **projects.json double-escape when writing from Python.** Keys are Windows paths
  stored with single backslashes in the JSON file: `"c:\\laragon\\www\\IBT"`. Writing
  via `json.dump` with a Python literal `'c:\\\\laragon\\\\www\\\\ibt'` yields
  `c:\\\\laragon` (double-escaped) — IDE won't match it. Use a single-backslash Python
  string (`"c:\\laragon\\www\\IBT"`) so the JSON gets one escape level. Always
  `grep` the key back after writing and confirm it matches existing entries.
- **IDE caches customizations per session.** New skills / edited `skills.json` need IDE restart or
  "Reload Window" before they appear.
- **Docs on the machine are the source of truth.** Web docs (antigravity.google) describe the CLI
  layout (`~/.gemini/antigravity-cli/skills/`, `~/.../plugins/`); builtin `agy-customizations/docs/*.md`
  describe what the IDE actually reads. When they differ, trust builtin.

## Verification

1. In agent chat, type `/` — registered skills appear as slash commands.
2. Ask the agent: "list semua skill yang kamu punya di project ini" — loaded skills get named.
3. Filesystem: confirm `SKILL.md` exists in the expected scope dir and frontmatter is valid.
4. If absent: restart IDE → reopen project → re-check `/`.

## Skill authoring rules (from builtin docs)

- `description` is the most critical field: agent uses it to decide activation. State what + when.
- Progressive disclosure: keep SKILL.md concise, push bulky detail into `references/`.
- Executable helpers in `scripts/` referenced by relative links.
- Include validation steps in the skill body.
- Do not duplicate general coding knowledge the agent already has.