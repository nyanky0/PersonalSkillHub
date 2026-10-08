---
name: hermes-agent-suite
description: "Comprehensive Hermes Agent orchestration, theming, custom pets, token optimization, and subprocess CLI management."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [hermes, agent, theming, persona, pets]
---

# Hermes Agent Suite



## Sub-Module: hermes-agent

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, a native desktop app, messaging platforms, and IDEs. It's in the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, Google, DeepSeek, xAI, local models, and 20+ others) and runs on Linux, macOS, Windows, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills that load into future sessions.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, iMessage, Signal, Matrix, Teams, Email, and a dozen more platforms with full tool access, not just chat.
- **Many surfaces** — the same agent core drives the CLI, the Ink TUI, a native Electron desktop app, a web dashboard, and an ACP server for IDEs (VS Code / Zed / JetBrains).
- **Provider-agnostic** — swap models and providers mid-workflow; credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible & themeable** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, skins that theme every surface, desktop UI plugins, TUI widgets, and pet mascots.

**This skill is a hub.** The body covers identity, quick start, spawning/orchestration, and hard invariants. Everything else lives in reference files — **load the matching reference (below) before answering**; do not answer detail questions from the body alone.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Scope & Verification

This skill is a concise operating guide, not the complete source of truth for every Hermes feature. If a Hermes feature, command, or setting is not mentioned here or in a reference, do not treat that absence as evidence that it does not exist. Check the live repository and official docs before giving a negative answer.

Good verification targets, cheapest first:

- **Every shipped feature, one line each: https://hermes-agent.nousresearch.com/docs/llms.txt.** Start here for any "can Hermes do X?" or "how do I do X?" — it indexes the entire documentation set with a link to the page that answers. It is generated from the docs tree on every build, so it is never behind the product. Fetch it with `web_extract`, or `curl -s https://hermes-agent.nousresearch.com/docs/llms.txt` when web tools are off. The whole documentation set in one file is at `/docs/llms-full.txt`.
- CLI commands: `hermes --help`, `hermes <command> --help`, and `hermes_cli/main.py`
- Source tree: https://github.com/NousResearch/hermes-agent

Never answer "Hermes can't do that" from memory. Hermes ships far more than this skill body describes, and the index exists so a negative answer is always checkable.

## Quick Start

```bash
# Install (shell installer — sets up uv, Python, the venv, and the launcher)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Interactive chat (default surface; set display.interface: tui to launch the Ink TUI instead)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard  /  pick model+provider  /  health check
hermes setup
hermes model
hermes doctor

# Other surfaces
hermes desktop                 # launch the native desktop app (alias: hermes gui)
hermes dashboard               # web admin panel + embedded chat
hermes proxy                   # OpenAI-compatible local proxy backed by your OAuth provider
```

## Key Paths

```
~/.hermes/config.yaml       Main configuration (settings — never secrets)
~/.hermes/.env              API keys and secrets ONLY (under $HERMES_HOME if set)
$HERMES_HOME/skills/        Installed skills
~/.hermes/skins/            Custom themes (see references/themes.md)
~/.hermes/desktop-plugins/  Desktop app UI plugins (see references/desktop-plugins.md)
~/.hermes/tui-widgets/      TUI widget apps (see references/tui-widgets.md)
~/.hermes/pets/             Installed pet mascots (see references/petdex.md)
~/.hermes/state.db          Canonical session store (SQLite + FTS5)
~/.hermes/sessions/         Gateway routing index, request dumps, *.jsonl transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout. When a profile is active, resolve the real home from `$HERMES_HOME` — never hardcode `~/.hermes`.

## Routing Table — load the reference for the task

| User wants... | Load |
|---|---|
| **Anything not listed below — "can Hermes do X?", "how do I set up X?"** | **https://hermes-agent.nousresearch.com/docs/llms.txt** |
| Bots that chat, run routines, or message each other; the Bots tab | docs: `/user-guide/bot-mode` |
| CLI commands, subcommands, flags, "how do I run X" | `references/cli-reference.md` |
| In-session slash commands | `references/slash-commands.md` |
| Provider setup, API keys, OAuth | `references/providers-and-models.md` |
| config.yaml sections, toolsets, voice/STT/TTS | `references/configuration.md` |
| AGENTS.md / .hermes.md / CLAUDE.md project rules | `references/project-context-files.md` |
| Secret redaction, PII, approval modes, "reset permissions" | `references/security-privacy.md` |
| Delegation, cron, curator, kanban | `references/background-systems.md` |
| MCP servers (add, catalog, `hermes mcp`) | `references/native-mcp.md` |
| Webhook routes and event-driven runs | `references/webhooks.md` |
| A custom theme/skin ("synthwave theme", "change the gold ●") | `references/themes.md` + `templates/skin.yaml` |
| A desktop app UI element (pane, widget, ⌘K command, page) | `references/desktop-plugins.md` + `templates/plugin.js` |
| A live TUI panel or modal widget (ticker, clock, dashboard) | `references/tui-widgets.md` + `templates/clock.mjs` |
| Pet mascots — install, select, scale, diagnose | `references/petdex.md` |
| Windows-specific issues (keybinds, WinError 10106, BOM) | `references/windows-quirks.md` |
| Debugging: voice, tools missing, gateway, aux models | `references/troubleshooting.md` |
| Contributing code: adding tools, slash commands, tests | `references/contributor-guide.md` |
| delegate_task "capped at N" reports | `references/delegate-task-concurrency-diagnosis.md` |
| "Can app X use my Nous Portal subscription/OAuth?" | `references/portal-auth-for-third-party-apps.md` |
| Connecting a messaging platform (Telegram, Discord, Slack, WhatsApp, …) | docs: `/user-guide/messaging` |

The reference list above is not the feature list — it is the set of topics that
need more than their docs page. For everything else Hermes ships, fetch
`llms.txt` and it maps the question to the page that answers it.

Two theming rules that hold even without loading the reference: **you apply skins yourself** (`hermes config set display.skin <name>` — every surface repaints live within ~a second; don't tell the user to run `/skin`), and **to tweak one color, edit the ACTIVE skin** (`hermes skin set <key> <hex>`) — never fork `default`, which drops the palette and resets the background.

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry
- **"delegate_task is capped at N" reports** — see `references/delegate-task-concurrency-diagnosis.md`. Three real cap paths in Hermes; if none fired, the model is self-limiting and rationalising it as "the runtime caps."
- **"Can $external_app use my Nous Portal subscription / OAuth?"** — see `references/portal-auth-for-third-party-apps.md`. Walk the user through three layers (plugin-vs-app, what Portal actually exposes, local-broker-proxy option).

## Surfaces (quick orientation)

- **Desktop app** (`hermes desktop` / `hermes gui`) — native Electron app for macOS/Linux/Windows: streaming chat, session list, Cmd+K palette, drag-and-drop files, native notifications, per-profile remote-gateway login. Extend it with UI plugins — `references/desktop-plugins.md`.
- **Web dashboard** (`hermes dashboard`) — full admin panel: messaging channels, MCP catalog, webhooks, memory, profile builder, plus an embedded `hermes --tui` chat. Secured behind an OAuth/token gate.
- **Ink TUI** (`hermes --tui` or `display.interface: tui`) — terminal UI with docked widget apps — `references/tui-widgets.md`.
- **OpenAI-compatible proxy** (`hermes proxy`) — a local OpenAI API backed by whichever OAuth provider you're signed into. Point Codex CLI, Aider, Cline, or any script at it — no API key.

## Hard Invariants (never violate, regardless of what you loaded)

- **Never break prompt caching** — don't change past context, toolsets, or the system prompt mid-conversation. The only exception is context compression.
- **Message role alternation** — never two assistant or two user messages in a row; only `tool` results can repeat.
- **Secrets in `.env`, settings in `config.yaml`** — never tell a user to put a non-credential setting in `.env`.
- **Profile-safe paths** — `get_hermes_home()` in code, `$HERMES_HOME` when resolving paths in a session.
- **Never hand-edit `config.yaml` for the user** — use `hermes config set KEY VAL`; a stray indent can corrupt the file and break the live gateway.

---

## Sub-Module: hermes-agent-skill-authoring

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `skills/<category>/<name>/SKILL.md` or `optional-skills/<category>/<name>/SKILL.md` inside the hermes-agent repo — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

In-repo skills must meet the repo's **hardline authoring standards** (see AGENTS.md, "Skill authoring standards (HARDLINE)" — that section is the source of truth; this skill is the operational walkthrough). Reviewers reject PRs that violate them, so meeting them up front is cheaper than a salvage pass later.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `skills/` or `optional-skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)
- Don't use for: personal skills in `~/.hermes/skills/` (just use `skill_manage`)

## Decide the Tier First: Bundled vs Optional

- **Bundled (`skills/<category>/`)** — daily-driver behavior, broadly useful across many user types, low footprint. Hard bar: you can say "a user will load this in 5+ sessions per month" with a straight face.
- **Optional (`optional-skills/<category>/`)** — niche, vertical-specific (blockchain, gaming, finance, one app), recurring-job/task skills, or anything heavy. Installed via `hermes skills install official/<category>/<skill>`.

**When in doubt, optional.** Promoting later is easy; demoting is churn. "Would be useful to anyone who ever needs this" is an optional-tier argument, not a bundled one.

Pick the category by what the tool IS, not what it feels like (an AI-agent CLI goes in `autonomous-ai-agents/` even if it "feels productivity"). Confirm existing categories with `search_files(pattern='*', target='files', path='skills')` and don't invent new top-level categories casually.

**No router / index / hub skills.** A skill whose core content is a routing table pointing at sibling skills adds an indirection hop and duplicates the siblings' own `When to Use` triggers. If the skill would be empty without "load skill X instead" pointers, don't write it — the catalog and each sibling's triggers already do that job.

## Required Frontmatter

Validator source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Validator hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present (validator ceiling 1024 chars — but see the repo hardline below, which is much stricter).
- Non-empty body after the closing `---`.

Repo-standard shape (all fields expected, even where the validator doesn't enforce them):

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Concise capability statement, under sixty chars.
version: 0.1.0                    # semver; new skills start at 0.1.0
author: Real Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]   # audit, don't guess — see Platform Gating
metadata:
  hermes:
    tags: [Short, Descriptive, Tags]
    related_skills: [other-in-repo-skill]
---
```

### `description` rules (HARDLINE — the validator's 1024 is NOT the standard)

- **≤ 60 characters.** One sentence. Ends with a period.
- State the capability, not the implementation, and don't repeat the skill name.
- No marketing words ("powerful", "comprehensive", "seamless", "advanced").
- The system prompt skill index truncates at 57 chars + "..." — the trigger/capability must be self-contained in that window.
- If the description contains a `:`, wrap it in double quotes or YAML parses it as a mapping and the docs generator crashes. Quotes don't count toward the 60.

Good: `Track named companies for material news with cited digests.`
Bad: `Use when a user asks to monitor named competitors or companies for product launches, pricing changes, funding, ...` (240 chars — rejected in review)

### `author` rules

- Credit the **human first**, then "Hermes Agent" as secondary collaborator: `Ben Barclay (benbarclay), Hermes Agent`.
- Never `author: Hermes Agent` alone for contributed skills — credit the human, not the tool, even (especially) when an agent drafted the text.
- Maintainer-authored skills: `Teknium (teknium1), Hermes Agent`.

### `related_skills` rules

- Every entry must resolve to an existing **in-repo** skill in the same tree state as your PR. Do not reference skills that were only planned, live in another PR, or exist only in `~/.hermes/skills/`.
- Verify each entry: `search_files(pattern='<name>', target='files', path='skills')` (and `optional-skills/`).

## Platform Gating: audit, don't trust

`platforms:` gates loading by host OS. Set it from what the skill's prose and scripts actually invoke:

| Skill uses only… | `platforms:` |
|---|---|
| Hermes tools + stdlib Python + cross-platform CLIs | `[linux, macos, windows]` |
| bash pipelines, `grep`/`awk`/`sed` chains, heredocs | `[linux, macos]` |
| `osascript`, `defaults`, `pmset` | `[macos]` |
| `apt`/`systemctl`/`/proc` | `[linux]` |

POSIX-only signals to search for in `scripts/`: `fcntl`, `termios`, `pty`, `os.fork`, `os.killpg`, `signal.SIGKILL`, `os.kill(pid, 0)` liveness checks, hardcoded `/tmp` `/proc` `/etc`. Default posture: fix cross-platform first (`tempfile.gettempdir()`, `pathlib.Path`, `psutil.pid_exists`); gate narrower only when the dependency is genuinely platform-bound, and say why in `## Pitfalls`.

## Size Limits

- Full SKILL.md: ≤ 100,000 chars enforced (`MAX_SKILL_CONTENT_CHARS`), but target **~100 lines for a simple skill, ~200 for a complex one**. Peer skills sit at 8-14k chars.
- Bulky or branch-specific material goes in `references/*.md`, `templates/`, or `scripts/` — pointed to from SKILL.md, not inlined.
- Don't expect the model to inline-write parsers or non-trivial logic every call — ship a helper script in `scripts/` and reference it by path.

## Body Structure (modern section order)

```
# <Skill> Skill
2-3 sentence intro: what it does, what it doesn't do, dependency stance.

## When to Use          — bulleted triggers (+ "Don't use for:" counter-triggers)
## Prerequisites        — exact env vars, installs, API key sourcing
## How to Run           — canonical invocation through the `terminal` tool
## Quick Reference      — flat command list, no narration
## Procedure            — numbered steps, each with a checkable completion criterion
## Pitfalls             — known limits, things that look broken but aren't
## Verification         — how to prove the skill worked
```

Not every section applies to every skill (a pure-procedure task skill may have no Quick Reference), but When to Use + actionable body + Pitfalls + Verification are the minimum. Cut marketing intros, "Setup Check" no-ops, and re-explanations of env vars already in Prerequisites.

### Reference Hermes tools, not raw shell

When the skill needs a capability, name the proper Hermes tool in backticks: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, `web_search`, `web_extract`, `browser_navigate`, `vision_analyze`, `delegate_task`, `cronjob`. Do NOT name shell utilities the agent already has wrapped (`grep` → `search_files`, `cat` → `read_file`, `sed`/`awk` → `patch`, `find`/`ls` → `search_files target='files'`). A CLI-wrapper skill should frame invocations as `terminal(command="<tool> ...", timeout=...)` — bare shell prose ("run `foo --version`") is a review-blocking non-conformance. If the skill depends on an MCP server, name it and document setup in Prerequisites.

### Never use machine-local paths

Write repo-relative paths (`skills/...`, `tools/skill_manager_tool.py`). A `/home/<you>/...` path baked into a committed skill breaks for every other user and is an instant review flag.

## Writing Quality Principles

A skill exists to make the agent's process more predictable — the agent reliably follows the same useful discipline.

1. **Optimize for process predictability.** If a line does not change behavior, cut it.
2. **Choose the right context load.** The description is paid for every turn; details go in the body or linked references.
3. **End steps with completion criteria.** Checkable and, when it matters, exhaustive: "every modified file accounted for" beats "summarize changes."
4. **Co-locate rules with the concept they govern.**
5. **Use strong leading words** ("tight loop," "root cause," "regression test") over long repeated explanations.
6. **Prune duplication and no-ops.** "Be careful" and "use best practices" don't change model behavior — replace with a checkable criterion or delete.

## Tests and Docs (required for repo skills)

1. **Tests** live at `tests/skills/test_<skill>_skill.py` — stdlib + pytest + `unittest.mock` only, no live network. Run via `scripts/run_tests.sh tests/skills/test_<skill>_skill.py -q`. (The generic `tests/tools/test_skill_manager_tool.py` passing proves nothing about YOUR skill.)
2. **Docs regen:** run `python website/scripts/generate-skill-docs.py`, then apply scope discipline — the generator rewrites EVERY auto-gen page. `git checkout --` everything that isn't yours; the final diff must show only your SKILL.md, your one per-skill docs page, a one-line catalog row, and a one-line `website/sidebars.ts` insertion (verify with `search_files(pattern='<your-slug>', path='website/sidebars.ts')` — exactly one hit, or the page is an orphan).
3. **`.env.example`** (only if the skill needs new env vars): one clearly delimited commented block; touch nothing else in the file.

## Workflow

1. **Survey peers** in the target category with `search_files(target='files')` and read 2-3 peer SKILL.md files to match tone and structure. Prefer extending an existing skill over creating a narrow sibling.
2. **Decide tier and category** (see above). When in doubt, optional — and ask before pushing rather than defaulting.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md` (or `optional-skills/...`).
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 60, f"description {len(fm['description'])} chars — hardline is 60"
   assert fm["description"].endswith(".")
   assert "platforms" in fm
   assert len(content) <= 100_000
   ```
   Also verify every `related_skills` entry exists in-repo.
5. **Add tests + regen docs** (previous section).
6. **Git add + commit** on the active branch; open a PR.
7. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Editing Existing In-Repo Skills

- **Small fix:** `skill_manage(action='patch', ...)` works on in-repo skills, as does `patch`.
- **Major rewrite:** `write_file` the whole SKILL.md.
- **Supporting files:** `write_file` to `references/`, `templates/`, or `scripts/` under the skill dir.
- **Always commit** — in-repo skills are source, not runtime state. Re-run the docs generator when frontmatter changed.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file`.
2. **Trusting the validator's limits as the standard.** The validator allows 1024-char descriptions; review rejects anything over 60. The validator doesn't check `platforms:`, author format, tests, or docs — review does.
3. **`author: Hermes Agent` on a contributed skill.** Credit the human first.
4. **Leading whitespace before `---`.** Validation fails on any leading blank line or BOM.
5. **Description too generic or trigger buried past char 57.**
6. **`related_skills` pointing at skills that don't exist in-repo** (user-local, planned, or in a sibling PR).
7. **Duplicating a peer.** Survey the category first; extend rather than sibling.
8. **Skipping the docs generator or pushing its unrelated drift.** Both directions are wrong: no regen = orphan skill with no docs page; blind regen = a ballooned diff full of other skills' drift.
9. **Expecting the current session to see the new skill.** The loader is initialized at session start.
10. **Letting skills accumulate sediment.** When adding a rule, remove the old wording it replaces.

## Verification Checklist

- [ ] Tier decided deliberately (bundled bar: 5+ sessions/month; else `optional-skills/`)
- [ ] File at `skills/<category>/<name>/SKILL.md` or `optional-skills/<category>/<name>/SKILL.md`
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `platforms`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Description ≤ 60 chars, one sentence, ends with a period, no marketing words
- [ ] `author` credits the human contributor first
- [ ] `platforms:` audited against actual prose/scripts, not copied from a sibling
- [ ] Every `related_skills` entry resolves in-repo
- [ ] Body follows the modern section order; commands framed through Hermes tools
- [ ] No machine-local paths anywhere in the file
- [ ] Each ordered step has a checkable completion criterion
- [ ] Tests at `tests/skills/test_<skill>_skill.py` pass under `scripts/run_tests.sh`
- [ ] Docs regenerated with scope discipline; sidebar has exactly one entry for the slug
- [ ] `git add` + commit on the intended branch; PR opened

---

## Sub-Module: hermes-cli-subprocess

# Spawning `hermes chat` as a subprocess

Use when a Python/shell server or script kicks off a Hermes agent (PRD Studio `/send`, dev runners, agent pipelines, CI spawn). Covers the non-obvious CLI parsing quirk, process-liveness detection, and per-run log hygiene that make these runners silently "diam" (no agent spawned) or produce merged logs.

## Known-good command shape

```bash
hermes chat -q "Mulai project ini. Baca PRD.md, AGENTS.md dan tasks.md di folder ini..." --max-turns 60 --skills safe-code-authoring
```

**Query string goes IMMEDIATELY after `-q`, before any other flags.**

## Pitfall 1 (critical): argparse eats option-like tokens

`hermes chat` uses argparse. `-q` (and any option that takes a value) will NOT consume a following token that starts with `-`:

- FAIL: `hermes chat -q --max-turns 60 "query"` → `error: argument -q/--query: expected one argument`
- FAIL: `hermes chat --max-turns 3 -s safe-code-authoring "query"` → same error
- OK: `hermes chat -q "query" --max-turns 60 --skills safe-code-authoring`

The server dies silently (exit 0 from the shell wrapper's perspective) — the agent never spawns and run.log only shows the usage error. Symptom: "runlog diam". This is NOT a PATH problem; check the log tail for `usage: hermes chat` before anything else.

## Pitfall 2 (critical): zombie PID = "still running" false positive

Runner writes the spawned shell PID to `.run.pid`. After the agent exits, the shell can linger as a **zombie** (`Z`). `/proc/<pid>` still exists, so naive `Path(f"/proc/{pid}").exists()` returns True → runner thinks agent is alive → refuses to spawn a new one → "diam" again.

Correct liveness check — read state from `/proc/<pid>/stat` (3rd whitespace field):

```python
def _alive(pidfile):
    try:
        pid = int(pidfile.read_text().strip())
    except Exception:
        return False
    try:
        with open(f"/proc/{pid}/stat") as f:
            st = f.read().split()
        return len(st) > 2 and st[2] != "Z"
    except Exception:
        return False
```

Use this everywhere the runner decides "is an agent already running?" (`/log`, `/run`, `/send` handlers).

## Pitfall 3: log concatenation across runs

Open run.log with `'w'`, not `'a'`. Append mode merges every dev run into one growing file — user sees "runlog gabung dengan yang sebelumnya". Fresh `'w'` per spawn = fresh log per PRD/dev run.

## Pitfall 4: which hermes to invoke

On this user's machine: `~/.local/bin/hermes` is the bash wrapper (`unset PYTHONPATH; unset PYTHONHOME; exec ~/.hermes/hermes-agent/venv/bin/python ~/.hermes/hermes-agent/hermes "$@"`). Use it. The bare `~/.hermes/hermes-agent/hermes` script needs the venv python on PATH (imports `hermes_cli`). `shutil.which("hermes")` from a spawned server env can resolve elsewhere or miss — hardcode the wrapper path or resolve once at server start.

## Spawn pattern (Python server)

```python
logf = proj / "run.log"
with open(logf, "w", encoding="utf-8") as lf:
    lf.write("[runner] hermes mulai: " + str(datetime.now()) + "\n")
cmd = f'{HERMES} chat -q "{PROMPT}" --max-turns {MAX_TURNS} --skills safe-code-authoring'
lf = open(logf, "w", encoding="utf-8")
pobj = subprocess.Popen(cmd, shell=True, cwd=str(proj), stdout=lf, stderr=subprocess.STDOUT)
pidfile.write_text(str(pobj.pid), encoding="utf-8")
```

## Verify a spawn actually started

1. `ps --ppid <pid>` → child `venv/bin/python ... hermes chat` must exist (state `S`/`D`, NOT `Z`).
2. `head run.log` → first line `Query: ...` (not `usage: hermes chat`).
3. After ~10s, log grows with tool calls (`read PRD.md`, etc.).

## Resume / handoff

run.log footer prints `Resume this session with: hermes --resume <session-id>` — surface that to the user so they can continue the agent session.

## Testing the HTTP endpoint without shell-quoting hell

Multiline JSON inline in `curl -d` breaks. Write payload to a temp file, then `--data @file`:

```bash
printf '%s' '{"name":"test","files":{"PRD.md":"...","AGENTS.md":"..."},"auto_run":true}' > /tmp/t.json
curl -s -X POST http://localhost:8678/send -H 'Content-Type: application/json' --data @/tmp/t.json -o /tmp/resp.json
```

Also avoids the `curl | python3 -m json.tool` pipe-to-interpreter security flag.

Concrete instance: PRD Studio runner — see `references/prd-studio.md`.

## Serving agent-built HTML so the user can view it

User on Windows wants to open `~/prd-outbox/<slug>/index.html` in a browser. `wslview` isn't installed; `explorer.exe <wslpath>` no-ops; `cmd.exe /c start` refuses UNC `\\wsl.localhost\...` paths. Durable answer: add a `/preview/<slug>/<file>` route to the runner's http.server (parse slug from the PATH, not the query string), then the user opens `http://localhost:8678/preview/<slug>/index.html`. Full route code + pitfalls (lazy-image false negatives, restart-before-debug) in `references/wsl-open-file-browser.md`.

---

## Sub-Module: hermes-custom-pets

# Custom Pet Creation for Hermes

## Overview
Petdex (https://petdex.dev) has ~4700 pets but may lack specific characters. Custom pets can be built from any animated sprite source (GIF, sprite sheet) by packaging into the petdex atlas format.

## Atlas Format (from `agent/pet/constants.py`)
- Grid: **8 columns × 9 rows** = 1536×1872 px
- Frame size: **192×208 px** each
- File: `spritesheet.webp` (lossless WebP preferred, ~6KB for simple pixel art)
- `pet.json`: `{"id": "<slug>", "displayName": "<Name>", "description": "<desc>", "spritesheetPath": "spritesheet.webp"}`

## Row Taxonomy (top→bottom, CODEX_STATE_ROWS)
```
0: idle            5: failed
1: running-right   6: waiting
2: running-left   7: running
3: waving          8: review
4: jumping
```
Only first **6 columns** per row are consumed (FRAMES_PER_STATE=6). Loop duration: 1100ms.

## Steps

1. **Search petdex first** — `hermes pets list <keyword>`. If found, `hermes pets install <slug>`. Skip custom creation.
2. **Find sprite source** — search web for `<character> pixel art sprite sheet GIF transparent`. Good sources: DeviantArt (pixel art GIFs), pngitem.com, spriters-resource.com (Cloudflare-blocked from browser automation).
3. **Download sprite** — terminal curl/Python often fail DNS resolution in WSL. Use browser fetch + trigger download:
   ```js
   // browser_console expression
   (async () => {
     const resp = await fetch("<img_url>");
     const blob = await resp.blob();
     const arrayBuf = await blob.arrayBuffer();
     const u8 = new Uint8Array(arrayBuf);
     let binary = '';
     for (let i = 0; i < u8.length; i++) binary += String.fromCharCode(u8[i]);
     const b64 = btoa(binary);
     const a = document.createElement('a');
     a.href = 'data:image/png;base64,' + b64;  // or image/gif
     a.download = '<filename>';
     document.body.appendChild(a);
     a.click();
     document.body.removeChild(a);
   })()
   ```
   File lands in `~/Downloads/` (WSL path) or browser download location.
4. **Extract frames** — if GIF, use PIL (`~/.hermes/hermes-agent/venv/bin/python3` has PIL):
   ```python
   from PIL import Image
   gif = Image.open("<path>")
   for i in range(gif.n_frames):
       gif.seek(i)
       frame = gif.convert('RGBA')
       # process frame
   ```
5. **Process each frame**:
   - Crop to content bounding box (remove whitespace)
   - Scale to fit 192×208 maintaining aspect ratio (NEAREST resampling for pixel art)
   - Center on 192×208 transparent canvas
6. **Build atlas** — paste frames into 1536×1872 grid. For rows where you lack source animation (running, jumping, etc.), reuse idle frames with variations (flip horizontal, darken for failed state).
7. **Install**:
   ```bash
   mkdir -p ~/.hermes/pets/<slug>
   # copy spritesheet.webp + pet.json
   hermes pets select <slug>
   hermes pets doctor
   ```
8. **Verify** — `hermes pets show` in TTY, or check `hermes pets doctor` says "ready".

## Pitfalls
- **DNS resolution from terminal fails often in WSL** — `curl`, Python `urllib`, `socket.getaddrinfo` all fail. Browser fetch + download trigger is the reliable workaround.
- **petdex names can be misleading** — `xiao-xiao-gwen` is Gwen from League of Legends, NOT Spider-Gwen. Always verify sprite visually before installing.
- **Terminal CLI can't render pets** — `hermes pets show` needs TTY. Pet shows in desktop app and TUI only.
- **System python3 has no PIL** — use `~/.hermes/hermes-agent/venv/bin/python3` instead.
- **Cloudflare blocks browser automation on spriters-resource.com and itch.io** — use DeviantArt, pngitem.com instead, or manual download.
- **Scale** — default 0.33 is small. `hermes pets scale 0.5` for bigger pet.
- **vision_analyze may 502** — vision model (kimi-k3) intermittent. Save frame PNG to `/tmp/` and use `browser_vision` or copy to Windows Desktop for user inspection as fallback.

---

## Sub-Module: hermes-node-diagnostics

# Hermes Node/JS Bootstrap Diagnostics

Hermes ships several surfaces whose deps are installed with **npm** at runtime, not pip:
the Ink TUI (`hermes --tui` / `display.interface: tui`), the Electron desktop app, the web
dashboard, some gateway bridges (e.g. WhatsApp bridge), Camofox browser server, and LSP JS
servers. When one of these bootstraps by running `npm install` inside the checkout, a failed
install typically surfaces as a bare **`npm install failed.`** with **no error detail**.

This skill is the diagnostic path for that class of failure. It is NOT a claim that npm is
broken — the root cause is almost always a version/engine constraint or a missing dependency.

## Notes on the bundled hermes-agent skill

The bundled `hermes-agent` skill is the authoritative Hermes reference but is READ-ONLY
(pinned/bundled — do not edit it). This skill records the probing workflow and pitfalls that
frequently bite during Hermes Node-dependency bootstraps.

## Diagnostic workflow (do these in order — step 2 usually nails it)

1. **Check the exact place where npm failed.** The failure lives in
   `<HERMES_HOME>/hermes-agent/hermes_cli/main.py` (grep `npm install failed`). It wraps the
   install via `subprocess.run(..., stdout=STDOUT, stderr=PIPE)` and only retries through the
   auto-repair in `hermes_cli/npm_engine.py` when the captured output is non-empty.

2. **Read the npm engine/engines constraint — the #1 root cause.** The repo root
   `package.json` sets strict `engines` (e.g. `{"node": ">=22.22.0", "npm": "<11.10.0 || >=11.17.0"}`)
   and the checkout's `.npmrc` sets `engine-strict=true`. If the actual system npm is outside
   that range, every npm install aborts with `EBADENGINE`. Reproduce it:
   `cd <HERMES_HOME>/hermes-agent/ui-tui && npm install` (ui-tui is the TUI workspace) to force
   the real error out. Confirm the actual version with `npm --version`.

3. **If EBADENGINE: align npm to the required range, then re-run the failing surface.**
   Never guess — read `engines` from the root `package.json`. Hermes' own repair
   (`maybe_repair_npm_engine` in `npm_engine.py`) upgrades a **managed** npm in
   `$HERMES_HOME/node` in place, else provisions a managed Node tree; it deliberately NEVER
   touches a system/nvm/brew/Nix npm (see `_print_manual_fix`). Fastest benign fix for a system
   npm is a minimal version bump to the nearest allowed range, e.g.
   `npm install -g npm@<range-min>` (prefer the nearest patch ≥ the `>=` bound over jumping to a
   new major — v12+ can carry breaking changes). Then re-run `hermes --tui`.

4. **If not an engine mismatch**, inspect `$LOCALAPPDATA/npm-cache/_logs/*-debug-0.log` (Windows)
   or the path reported in the error — the npm debug log records the full argv, the resolved
   cwd, and the exact `npm error code` (ENOWORKSPACES, EACCES, missing registry, etc.).

## Pitfalls (learned the hard way)

- **`--silent` can swallow the entire EBADENGINE message.** Hermes runs its TUI npm install with
  `--silent --no-fund --no-audit --progress=false`. Because `_run_tui_install()` captures
  stdout/stderr, on some npm builds the EBADENGINE text never reaches the captured output, so
  `is_ebadengine(output)` in `npm_engine.py` sees an empty string, the auto-repair never
  triggers, and you get only the bare `npm install failed.` — no fix suggestion, no version
  mismatch detail. Reproduce the command WITHOUT `--silent` (or copy it from the source, lines
  around `npm_install_cmd = [...]`) to surface the true error.
- **Verify the fix with a real TTY in mind.** After `npm install` succeeds, launching `hermes --tui`
  from a non-interactive/non-TTY shell prints `hermes-tui: no TTY` and exits 0. That is SUCCESS
  (deps installed + TUI built) — not a failure. In a real terminal the TUI opens normally.
- **ui-tui workspace location** on this repo layout: `<HERMES_HOME>/hermes-agent/ui-tui`
  (`hermes-tui@0.0.1`, deps `@hermes/ink`, `ink-text-input`, `esbuild`, `typescript` in
  devDependencies). `_workspace_root()` walks up to the nearest `package-lock.json` — ui-tui has
  none, so the resolved workspace root is the repo root and npm runs with `--workspace ui-tui`.

## References
- `references/2026-09-npm-ebadengine-tui.md` — end-to-end case: npm 11.16.0 outside range →
  bare "npm install failed." → diagnosis → `npm install -g npm@11.19.1` → resolved.

---

## Sub-Module: hermes-personality-config

# Hermes Personality Config (semua surface)

Prosedur mengubah/menambah persona Hermes yang berlaku untuk **semua tipe**
(CLI, TUI, desktop app, gateway) karena semua membaca config yang sama.

## Lokasi & struktur

File: `$HERMES_HOME/config.yaml` (`C:\Users\<user>\AppData\Local\hermes\config.yaml`)
(profile lain: `$HERMES_HOME/profiles/<name>/config.yaml`)

```yaml
agent:
  personalities:
    <nama-persona>:            # definisi persona
      description: ...
      system_prompt: '...'     # instruksi utama (biasanya multiline)
      tone: ...
      style: ...
display:
  personality: <nama-persona>  # persona AKTIF (yang dipakai semua surface)
```

Personality yang aktif dipakai di system prompt setiap sesi baru; CLI, TUI,
desktop, dan gateway semuanya membaca key yang sama.

## Ubah persona aktif (fast path)

```bash
# 1. Lihat config saat ini
grep -A8 "personalities:" "$LOCALAPPDATA/hermes/config.yaml"

# 2. Set system_prompt baru (pakai file biar aman dari quoting shell!)
cat > /c/tmp/prompt.txt <<'EOF'
...isi system_prompt baru (boleh multiline)...
EOF
hermes config set agent.personalities.<nama>.system_prompt "$(cat /c/tmp/prompt.txt)"

# 3. Set tone & style
hermes config set agent.personalities.<nama>.tone "super ceria, manja, ..."
hermes config set agent.personalities.<nama>.style "bahasa Indonesia informal, ..."

# 4. Aktifkan (kalau nama persona baru)
hermes config set display.personality <nama>

# 5. Verifikasi
grep -A10 "personalities:" "$LOCALAPPDATA/hermes/config.yaml"
grep "^  personality:" "$LOCALAPPDATA/hermes/config.yaml"
```

## Tambah persona baru (jangan timpa yang lama)

1. Tambah block `agent.personalities.<nama-baru>.*` (system_prompt/tone/style)
   dengan `hermes config set` (lihat atas).
2. Set `display.personality` ke nama baru.
3. Persona lama tetap ada di config — tinggal ganti `display.personality`.

## Aturan penting

- **JANGAN edit config.yaml manual** — selalu `hermes config set KEY VAL`
  (invariant Hermes; edit manual bisa korup YAML dan merusak gateway).
- **System prompt multiline**: simpan ke file temp lalu `$(cat file)` — lebih
  aman daripada quoting emoji/kaomoji/kutip di shell.
- **Efek pada sesi**: perubahan berlaku untuk **sesi baru** (`/reset` atau
  restart), bukan percakapan berjalan (jaga prompt caching).
- **Key yang tidak dikenal** mungkin di-notice; pakai `--force` kalau yakin.
- `hermes config check` untuk cek bagian config yang hilang/kedaluwarsa.

## Pasca-update

- Sesi baru otomatis pakai persona baru (CLI `hermes`, TUI `hermes --tui`,
  desktop `hermes desktop`, gateway sama).
- Kalau user juga mau gaya yang sama di sesi berjalan → update juga
  **user profile** lewat tool memory (target=user) dengan ringkasan gaya.

## Verifikasi

- `hermes config get display.personality` (kalau ada) atau grep config.yaml.
- Buka sesi baru, lihat system prompt/tonya berubah.
- `hermes doctor` untuk cek kesehatan config secara umum.

---

## Sub-Module: hermes-pet-customization

# Hermes Pet Customization

Customize installed Hermes pets: AI upscale to HD, swap/replace spritesheets,
fix blur/cropped rendering, and revert to stock. This skill drives the
filesystem + source-level knowledge behind `hermes pets` (whose CLI is covered
by the bundled `hermes-agent` skill's petdex reference — read that first for
install/select/scale commands).

## When to Use

- User wants the pet HD / less blurry / bigger without pixelation.
- User wants to replace a pet's sprite art.
- A pet renders cropped, misaligned, or quarter-size after a sheet swap.
- Reverting a customized pet back to stock.

## Pet Store Layout

```
<HERMES_HOME>/pets/<slug>/
    pet.json            # {id, displayName, description, spritesheetPath, ...}
    spritesheet.webp    # (or .png — pet.json spritesheetPath says which)
```

`pet.json` `spritesheetPath` is authoritative; the store falls back to probing
`spritesheet.{webp,png}` / `sprite.{webp,png}`. On Windows HERMES_HOME is
`C:\Users\<user>\AppData\Local\hermes`.

## Spritesheet Format (petdex / Codex)

- Stock sheets: **8 columns × 9 rows of 192×208 px cells** (1536×1872).
- Rows map to states: idle, running-right, running-left, waving, jumping,
  failed, waiting, running, review (row taxonomy is inferred from sheet shape).
- Up to **6 frames per state**; trailing fully-transparent cells are padding and
  the renderer stops at the first blank column.
- The renderer crops cells at `FRAME_W`/`FRAME_H` and scales by `display.pet.scale`.

## ⚠️ Critical Pitfall — Frame-Geometry Coupling

The renderer's cell size is HARDCODED in the hermes-agent source:

- `agent/pet/constants.py` → `FRAME_W = 192`, `FRAME_H = 208`
- `agent/pet/store.py` → `_THUMB_FRAME_W = 192`, `_THUMB_FRAME_H = 208`

If you swap in an upscaled sheet (e.g. 2x → 384×416 cells) WITHOUT patching
both files to the new size, the renderer crops only the top-left quarter of
every cell → the pet renders broken/quarter-size. **Always patch both files to
match the new cell size.** Note to the user that hermes-agent updates/reinstalls
overwrite these patches.

## HD Upscale Workflow (Real-ESRGAN, verified)

1. **Backup first** (inside the pet dir):
   `cp spritesheet.webp spritesheet.original.webp`
2. Convert the sheet to PNG with Pillow (WebP input is fine).
3. Get the tool + models in ONE download: fetch
   `realesrgan-ncnn-vulkan-20220424-windows.zip` from the **main Real-ESRGAN
   repo** release v0.2.5.0
   (`https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0`). That zip
   bundles `models/` (realesr-animevideov3-x2/x3/x4, realesrgan-x4plus,
   x4plus-anime). Do NOT use the ncnn-vulkan repo's own releases (v0.2.0) —
   they ship the exe only, and the model files are not separately downloadable
   (the `.../models/<name>` release URLs 404).
4. Run (anime model for sprites, needs a Vulkan-capable GPU):
   `realesrgan-ncnn-vulkan.exe -i sheet.png -o sheet_hd.png -n realesr-animevideov3-x2 -s 2`
5. **Save the result as PNG, not lossless WebP.** Pillow
   `save(..., format="WEBP", lossless=True, method=6)` is extremely slow on
   large sheets (times out past 120s); `format="PNG", optimize=True` is fast,
   lossless, and renders identically. Write `spritesheet.png`, set
   `pet.json` `spritesheetPath` to it, remove the old sheet file.
6. Patch `constants.py` `FRAME_W/H` and `store.py` `_THUMB_FRAME_W/H` to the new
   cell size (2x → 384/416).
7. Re-tune scale: cells doubled, so a similar on-screen size is roughly half
   the old scale (`hermes pets scale 0.8` from a previous 1.2, e.g.).
8. Verify (see Verification).

## Revert to Stock

1. `cp spritesheet.original.webp spritesheet.webp`; delete the HD png.
2. Restore `pet.json` `spritesheetPath` → `spritesheet.webp`.
3. Revert the `constants.py` and `store.py` patches to 192/208.
4. Reset `hermes pets scale` to the user's previous value.
5. Run `hermes pets doctor` + frame verification.

## Verification

```bash
hermes pets doctor
# then, from the hermes-agent source dir:
python -c "
import sys, os; sys.path.insert(0,'.')
from agent.pet.constants import FRAME_W, FRAME_H
from agent.pet.render import state_frame_counts, PetRenderer
from agent.pet.constants import PetState
sheet = os.path.expandvars(r'%LOCALAPPDATA%/hermes/pets/<slug>/spritesheet.webp')
print(FRAME_W, FRAME_H, state_frame_counts(sheet))
print([f.size for f in PetRenderer(sheet, mode='kitty', scale=1.0)._frames(PetState.IDLE)][:1])
"
```

For the Hatsune Miku pet, healthy counts are:
`idle 6, wave 4, run 6, failed 6, review 6, jump 5, waiting 6`.

## Pitfalls

- A pet only shows once installed AND selected AND `display.pet.enabled: true`.
- The `unicode` half-block renderer blurs small sprites by nature (1 char = 2
  pixel taps). A kitty-graphics terminal (WezTerm/Ghostty) renders true pixels
  and is the sharpest mode; Windows Terminal / VS Code embedded terminal
  deliberately detect as `unicode` (renderer trusts `TERM_PROGRAM=vscode`).
- Never leave two sheet files with a stale `pet.json` pointer — the renderer
  uses `spritesheetPath`, everything else is ignored.
- Keep `spritesheet.original.webp` until the user confirms the new look; it is
  the only clean revert path.

## References

- `references/hermes-pet-internals.md` — source map of the pet renderer/store
  (exact paths, decode behavior, encoding modes).

---

## Sub-Module: hermes-skills-hub

# Hermes Skills Hub — discover & install

How to browse, search, inspect, tap, and install skills from the Hermes skills hub (90k+ skills across `official`, `clawhub`, `skills.sh`). Load this when the user asks to "install skill X", "install the pack Y", "add skills Z", or when resolving a hub skill identifier.

Companion to the bundled `hermes-agent` skill (its CLI reference lists the commands but NOT the resolution quirks below). `hermes-agent-skill-authoring` is the authoring side, not the install side.

## Core workflow

```bash
hermes skills browse                     # 90k+ skills, paged.
hermes skills search "QUERY"              # match name+description across all sources.
hermes skills inspect <identifier>        # preview SKILL.md + upstream metadata BEFORE installing.
hermes skills install <identifier> -y     # -y / --yes skips the confirm prompt (needed non-interactively).
hermes skills tap add owner/repo          # register a GitHub repo as a skill source.
hermes skills tap list                    # show configured taps.
```

`install`/`inspect` resolve short identifiers against listed sources. Ambiguous → the tool prints a candidate table with the FULL identifier to use.

## Identifier quirks (the real pitfalls)

- **A bare short name that matches search may NOT resolve on install.** When `install`/`inspect` returns `No exact match for '<id>'` and "Did you mean" lists a row whose identifier looks identical to what you typed, the resolver wants a **source-prefixed** form. Prefix with the source namespace shown in search: `clawhub/<name>`; official form is `official/<category>/<name>`; skills.sh form is `skills-sh/<owner>/<repo>/<name>`.
- **Same name exists under multiple sources.** Pick explicitly via the full identifier rather than guessing, e.g. `skills-sh/dietrichgebert/ponytail/ponytail` vs `ponytail` (clawhub).
- **`--json` is NOT a valid flag on `hermes skills inspect`** — returns `unrecognized arguments`. Drop it.
- A repo tapped via `hermes skills tap add` may not surface its SKILL.md files in `search` immediately; its skills are often already mirrored on `clawhub`/`skills.sh` — search that way first.

## Blocked installs (must handle, not force-bypass)

The security scanner (skills-guard) can block installs from community sources. A **dangerous verdict** (rules like `agent_config_mod, git_clone, sudo_usage, too_many_files, unpinned_npm_install`) surfaces as:
`Installation blocked: Blocked (community source + dangerous verdict, N findings). --force does not override a dangerous verdict.`

- Do NOT try `--force` — it explicitly cannot override a dangerous verdict.
- Treat it as a signal to find a **safer alternative skill** for the same domain instead. Run `hermes skills search "<domain>"` and `inspect` candidates; prefer ones whose scan reports `rules: none`. That path worked cleanly (blocked `ui-ux-pro-max` → clean `ui-design` + `ui-design-tips`).

Worked example + transcript: `references/hub-install-example.md`.

## Pitfalls recap
- Always `inspect` (not just `search`) before install to verify upstream source, trust level, and the scanned rules list.
- Don't treat a source-prefix failure as "skill doesn't exist" — it's an identifier-namespace issue, not a nothing-found result.
- Session progress (what got installed) belongs in session history via session_search, not memory.

---

## Sub-Module: hermes-token-optimization

# Hermes Token Optimization

Reduce token spend on Hermes sessions via config keys. All edits via `hermes config set KEY VAL` (never hand-edit config.yaml) — changes take effect in a NEW session (/reset), never mid-conversation (preserves prompt caching).

## Highest-impact levers (set these first)

1. `compression.proactive_prune_tokens` — deterministic, NO-LLM-call pruning of large tool results (default 0 = off). Critical for large-context models (DeepSeek 128K, etc.): the 50% threshold rarely fires, so old tool output rides in history and gets re-sent every turn. Set 48000 to reclaim early. Gates: only prunes results >`proactive_prune_min_result_chars` (8000), only commits when reclaiming >=`proactive_prune_min_reclaim_tokens` (4096) so prompt-cache breaks stay episodic. Built-in compressor only.
2. `compression.idle_compact_after_seconds` — time-based compaction (default 0 = off). Set 1800: a session resumed after 30 min idle compacts stale history before first reply, instead of re-reading full context every turn.
3. `agent.max_turns` — cap tool-call loop per turn (default 90). Prevents runaway fix-loops that burn tokens (e.g. the empty-parens strip loop that ran 49 min). Per-command override: `hermes chat -q --max-turns N`.
4. `model.context_length` — set explicitly (e.g. 131072 for DeepSeek). Compression threshold math depends on it.

## Less common but useful

- `compression.threshold` (0.5) — lower to 0.40 for earlier/more aggressive compaction. Quality trade-off.
- `compression.threshold_tokens` — absolute token cap; triggers at min(ratio threshold, cap).
- `compression.model_thresholds` — per-model overrides, substring match (longest wins). Small-context floor 0.75 applies for <512K models (raise-only).
- `compression.protect_last_n` (20) / `min_tail_user_messages` (1→3) — keep recent turns verbatim through compaction.
- `compression.max_attempts` (3→6) — for tool-schema-heavy sessions.
- `prompt_caching.cache_ttl` — ONLY effective for Anthropic/OpenRouter. Custom providers (chat_completions) ignore it.

## Guardrail spawned agents (token + sanity)

When spawning autonomous `hermes chat -q` (PRD Studio bridge, cron, delegation):
- Always pass `--max-turns N` (bounded work; default 500 is a runaway risk).
- Preload `--skills safe-code-authoring` for code-generation tasks — prevents the empty-parens-strip fix loop.
- Embed stack/scope constraints IN the prompt ("single-file static HTML, no framework/build step") — agents otherwise over-engineer landing pages into full-stack apps.

## Verify

```bash
hermes config set compression.proactive_prune_tokens 48000
hermes config set compression.idle_compact_after_seconds 1800
hermes config set agent.max_turns 90
hermes config set model.context_length 131072
grep -A12 "^compression:" ~/.hermes/config.yaml
```

## Pitfalls

- `compression.proactive_prune` breaks the provider prompt-cache prefix on each commit — the min_reclaim gate keeps breaks episodic. Don't set min_reclaim below ~4096.
- Config edits apply to NEW sessions only; editing mid-session breaks prompt caching.
- Skills (llm-wiki, etc.) do NOT auto-load per prompt — they're lazy-loaded by relevance. Loading all skills per prompt would INCREASE tokens. Don't try to "preload everything" for savings.
- tamp / oc-context-optimizer target OpenClaw, not Hermes — do not propose them as Hermes solutions.

## References

- `references/context-compression-config.md` — full key semantics from agent/context_compressor.py + config_defaults.py

---

## Sub-Module: user-personality

# User Personality & Style

## Mahpud Persona
- Casual Indonesian (gue/lo/lu)
- Direct, no fluff
- Sparing partner — challenge ideas, don't just agree
- Professional but relaxed

## Style Rules
- **Active: terse caveman** — system prompt default aktif
- Drop artikel (a/an/the), filler (just/really/basically/actually/simply), pleasantries, hedging
- Pattern: [thing][action][reason]. [next step]
- Fragments OK
- Code paths, commands, errors, URLs: keep exact
- Exception: security warnings, irreversible actions, multi-step sequences — write normal
- Non-trivial logic leaves ONE runnable check (assert-based self-check or small test file)
- Active every response, no drift back to over-building
- No self-reference, no "me caveman think", no "compressed mode active"
- No decorative emoji
- No narrating tool calls ("I will now...", "Using X to...")
- No status phrases ("Sure!", "Of course!", "I'd be happy to")
- Resume terse style after clear exception parts

## Bahasa Indonesia
- Casual sehari-hari (gue/lo/lu)
- Langsung ke inti
- Challenge ideas, testing logic
- Tidak iya-in doang

## Location
- Full persona: `/home/maulana/soul.md`

---

## Sub-Module: session-librarian

# Session Librarian

Manage the user's session library conversationally: find past sessions about a
topic, summarize what they decided, rename them meaningfully, split work into
parallel sessions, and propose stale ones for archive or deletion — all from a
plain-language request like *"find my sessions about Q3 pricing, keep the
useful ones, and clean up the duplicates."*

Inspired by Perplexity Computer's prompt-driven session management (Aug 2026):
the agent starts, organizes, and cleans up the user's own session library, and
always shows the plan before touching anything.

## When to Use

- "What sessions do I have about X?" / "What did we decide about X?"
- "Rename these sessions to something meaningful."
- "Clean up my session library" / "archive the stale ones."
- "Fork that session into a follow-up focused on Y."
- "Split this into one session per ticket" (see Parallel workstreams below).

## The Two Surfaces

| Task | Surface |
|---|---|
| Find sessions by topic, read content, summarize decisions | `session_search` tool (FTS5 over the message store) |
| List/filter by metadata (age, source, cost, tokens, workspace) | `hermes sessions list` / `stats` via terminal |
| Rename | `hermes sessions rename <session_id> <title...>` |
| Bulk soft-hide (reversible) | `hermes sessions archive <filters>` |
| Delete (destructive) | `hermes sessions delete` / `hermes sessions prune <filters>` |
| Export before deleting anything valuable | `hermes sessions export --session-id <id> --format md` |
| Continue work in a new place | `/branch` (fork current session) or start a fresh session and cite the summary |

## Procedure

① **Discover.** Use `session_search(query=..., limit=5-10)` with topic
keywords; vary phrasing (feature name, symptom, project name). For metadata
sweeps ("sessions older than 60 days from telegram"), use
`hermes sessions list --source telegram --limit 50` instead.

② **Summarize per session.** The discovery result's `bookend_start` (goal),
match window, and `bookend_end` (resolution) usually suffice — only dump a
full session (`session_search(session_id=...)`) when the user asks for
decisions in depth. Report each as: link (`@session:` form) — one-line goal —
one-line outcome.

③ **Plan before acting (MANDATORY for anything that mutates).** Present a
plan table first: which sessions get renamed to what, which get archived,
which are proposed for deletion and why (duplicate of which keeper, stale,
empty). Wait for the user's go-ahead. Exception: a single rename the user
explicitly dictated can be done directly.

④ **Act with the safest primitive.**
- Prefer `archive` (reversible soft-hide) over `delete`/`prune`.
- Always run destructive commands with `--dry-run` first and show the output,
  then re-run with `--yes` after confirmation.
- Before deleting anything with meaningful content, offer
  `hermes sessions export --format md` as a backup.

⑤ **Report.** Renames applied, sessions archived (count + how to undo:
archived sessions remain in the DB and are listed with `--include-archived`),
anything exported, anything skipped and why.

## Parallel Workstreams

For "one session per ticket, investigate each, report back": do NOT try to
drive other live sessions. Use `delegate_task` with one task per workstream —
each subagent runs in its own session automatically — then synthesize their
summaries. Mention that each delegation's transcript is itself searchable
later via `session_search`.

## Restoring a session from a JSONL dump

A `session_export_*.jsonl` with per-line `{"role": ..., "content": ...}` (no `id`/`model` metadata) is a **Hermes-native dump**, NOT a Claude/Codex file — `hermes sessions import --from claude|codex` silently skips every line (parser wants `type`/`message` wrappers). Restore directly via SessionDB so tool messages survive:

```python
# venv: E:/HERMES/hermes-agent/venv/Scripts/python.exe, run from E:/HERMES/hermes-agent
import json, sys, time
sys.path.insert(0, r"E:/HERMES/hermes-agent")
from hermes_state import SessionDB
sid = time.strftime("%Y%m%d_%H%M%S") + "_restored"
db = SessionDB(); db.create_session(sid, source="desktop")
msgs = [json.loads(l) for l in open(r"<path>", encoding="utf-8") if l.strip()]
for m in msgs:  # keep role user/assistant/tool as-is; append_message accepts any role
    db.append_message(sid, m["role"], m.get("content") or "")
db.set_session_title(sid, "<title>")  # optional
print(sid)
```

Verify: `hermes sessions list` shows it, `hermes sessions export --session-id <id> --format jsonl` round-trips the same role counts. Resumable via desktop sidebar or `hermes --resume <id>`. Session id must be `YYYYMMDD_HHMMSS_<suffix>` format (created fresh each run — don't reuse an id that may exist).

## Pitfalls

- **Never delete without a dry-run + explicit confirmation in this
  conversation.** A standing "clean things up" is authority to *propose*, not
  to prune.
- **`session_search` finds content, not metadata.** Age/cost/source filters
  live in the CLI; combine both when the request mixes them ("old sessions
  about pricing").
- **Titles are identity for `/resume <title>`.** When renaming, keep titles
  short, unique, and prefix-friendly; warn the user if a rename collides with
  an existing title.
- **Archived ≠ deleted.** Archive hides sessions from default listings only.
  Say which one you did.
- **Cross-profile session links** (`@session:<profile>/<id>`) are read-only
  from another profile; management commands act on the current profile's DB.

## Verification

After a cleanup pass, re-run the discovery query and `hermes sessions list`
to confirm the library reflects the plan (keepers present with new titles,
archived ones gone from the default listing).

---