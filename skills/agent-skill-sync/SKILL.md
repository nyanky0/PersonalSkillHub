---
name: agent-skill-sync
description: Use to sync agent skills across Hermes, Cline, Gemini.
---

# Agent Skill Sync (D:\SkillHub master library)

Maintain a **canonical master copy** of every agent skill on the local machine so that
all coding agents (Hermes, Cline/Antigravity, Gemini CLI) stay in sync, and a newly
trialled agent gets the exact same skills by pointing it at one folder.

## Layout (this user's Windows setup)

```
D:\SkillHub\
├── skills\            <- MASTER: flat, 1 folder = 1 skill (SKILL.md + all supporting files)
├── scripts\sync_skills.py  <- the sync tool
├── docs\MANIFEST.md   <- human-readable skill list
├── docs\MANIFEST.json <- machine-readable skill list (name, description, changed)
└── README.md          <- full guide
```

Agent skill dirs:
| Agent | Path |
|---|---|
| Hermes | `E:\HERMES\skills\` (env `HERMES_HOME`; fallback `%LOCALAPPDATA%\hermes\skills\` untuk install lama) |
| Cline / Antigravity | `C:\Users\yudah\.agents\skills\` |
| Gemini CLI | `C:\Users\yudah\.gemini\config\skills\` |
| **Antigravity CLI (`agy`)** | **tidak ada path sendiri** — baca dari `C:\Users\yudah\.agents\skills\` (folder yang SAMA dengan Cline). Jadi `push cline` otomatis juga menyebar ke agy. |
| **Master hub** | **`D:\SkillHub\skills\`** |

## Core commands (`python D:/SkillHub/scripts/sync_skills.py ...`)

- `collect` — pull skills from hermes+cline+gemini into the hub. Merge: files in the
  hub that are NEWER are not overwritten; missing/new info is added. Dedups by name
  (hermes > cline > gemini priority).
- `push <target>` — push hub skills to ONE target: `hermes|cline|gemini|<custom path>`.
  Custom path is how you seed a brand-new agent ("just point it at the hub").
- `pushall` — push hub to hermes + cline + gemini at once.
- `list` — show skills in the hub.
- `manifest` — regenerate docs/MANIFEST.{md,json}.

## THE critical rule (new skill → everywhere)

Whenever a NEW skill is created/installed ANYWHERE, it must reach ALL FOUR locations
(both agents AND the hub). Sequence:
1. `collect`  — pull the new skill from whatever agent got it into the hub.
2. `pushall`  — spread hub → hermes + cline + gemini.
3. `manifest` — refresh the manifest.

This is stored in memory too, but the workflow lives here. If the user says "ada skill
baru" or "remember to sync new skills", run all three.

## Installing a skills tarball backup (no-clobber + dedupe)

When a `hermes-skills-backup.tar.gz` (a full `skills/` dir from another install) arrives:
1. Extract to temp, then walk for `SKILL.md` — the skill name is the dir containing it; ignore everything else.
2. **Never copy hidden state**: `.usage.json*`, `.curator*`, `.hub/`, `.bundled_manifest` are per-install bookkeeping (stats, quarantine, backup) — copying them mixes another machine's data. Only skill folders.
3. Install only names NOT already present (no-clobber). For near-duplicate groups (4 docx variants, 3 ytmusic variants, 3 antigravity variants, 2 fdd, 2 prd, 2 wsl, 2 mnemosyne, 2 token-opt): keep ONE canonical folder, write each member's SKILL.md body (frontmatter stripped) into `canonical/references/<member>.md`, copy member subfolders no-clobber, and DON'T create the member folder. This dedupes without losing content.
4. **Skip by policy**: token-compression-proxy skills (`tamp`, `9router-*`, `bandel-combo-switch`) and hub-install dupes already covered (`hermes-skill-hub*` when `hermes-skills-hub` exists) — per user standing rule, never install request-path compression proxies.
5. Then `collect` → `pushall` → `manifest` (see Core commands) to spread to cline/gemini/agy. Hub/cline/gemini start with ~251 skills and dedupe by name, so no old variants linger.
6. Verify: count `SKILL.md` per location + `hermes skills list` (should read the new names). ~370 SKILL.md / ~340 unique names is expected after a big import.

## Pitfalls
- **Dangling / MSYS-target symlinks in the Hermes skills dir break the whole sync.** `rglob("SKILL.md")` walks every entry, so a single broken symlink (target gone, or target written MSYS-style `/c/Users/...` which Windows-native Python resolves as `C:\c\Users\...`) raises `FileNotFoundError` and kills `collect`/`pushall` before it does anything — and it breaks `skill_view` the same way. If sync or skill_view dies with `FileNotFoundError: E:\HERMES\skills\<name>`, sweep for dangling links first: `for n in E:/HERMES/skills/*; do [ -L "$n" ] && [ ! -e "$n" ] && echo "$n"; done`, then `rm` the dead ones before re-running.
- **Consolidation leaves dangling links behind.** When near-duplicate skills get merged into a canonical folder (e.g. `caveman`, `caveman-commit`, `caveman-help`, `caveman-review` → `caveman-suite`), the old symlinks stay pointing at the now-deleted targets. They are stale cruft, not real skills — safe to delete once you confirm the canonical skill exists in hub + all agent dirs.

## Design notes / why it's safe
- **Idempotent**: re-running is safe; same-and-newer files are never overwritten.
- **Merge over overwrite**: per-file, newer mtime wins.
- **Flat naming**: skill name = folder containing SKILL.md. Handles Hermes' nested
  category layout (e.g. `github/github-pr-workflow/SKILL.md` → `github-pr-workflow`)
  and flat layouts (Cline, Gemini) uniformly by walking for `rglob("SKILL.md")`.

## Verification
After a trial-agent push, confirm integrity: count folders = count SKILL.md in the
target, and spot-check key skills exist (`ls <target>/<name>/SKILL.md`). Example check
seen working: 206 folders → 206 SKILL.md, SAP skills present.

## Related
- `agent-skills-install` — the OTHER path: installing skills from the `npx skills`
  GitHub/skills.sh ecosystem. This skill (sync) is about the local master hub and
  pushing across agents; they combine (install via npx → then `collect`+`pushall`).