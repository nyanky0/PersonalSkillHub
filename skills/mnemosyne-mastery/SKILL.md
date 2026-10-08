---
name: mnemosyne-administration
description: "Use when Mnemosyne recall is empty or DB corrupt."
tags: [mnemosyne, memory, sqlite, fts5, hermes, agent-memory]
related_skills: [hermes-agent, mcp-integration]
version: 1.0.0
---

# Mnemosyne OSS — Administration & Repair

The `mcp__mnemosyne__*` deferred tools + Python SDK (`~/.venvs/mnemosyne`) provide a local SQLite memory store at `~/.hermes/mnemosyne/data/mnemosyne.db`. This skill covers the ARCHITECTURE and REPAIR playbook — knowing how banks/DBs/FTS actually work prevents "data lost" panics and corrupting the store with raw SQL.

## Architecture (read first — this explains every "0 results" scare)

- **Each BANK = its own separate SQLite file.** `~/.hermes/mnemosyne/data/banks/<bank>/mnemosyne.db`. Banks on this machine: `working_memory` (agent working notes), `user_context` (user profile), `memory` (legacy imports).
- The top-level `data/mnemosyne.db` is the **default-bank** DB — `mnemosyne_get_stats` reads THIS one and reports 0 when all real data lives in per-bank files. A "0 memories" stat does NOT mean data loss; query per-bank.
- **The MCP tools (`mnemosyne_recall`/`get_stats`) operate on bank `default` by default** — they DO accept a `bank` arg in their schema, but Hermes calls them without one → `_resolve_bank()` falls back to `"default"` (the empty top-level DB) → 0 results. Since the 2026-09 fix, `_resolve_bank` defaults to `working_memory` and `_handle_recall` loops all banks + dedups when no explicit bank given. Bridge (below) is the other working recall path.
- **`MNEMOSYNE_DB_PATH` in `~/.hermes/config.yaml` was WRONG (2026-09 root cause of `mnemosyne_recall` → 0):** pointed at `~/.hermes/data/mnemosyne.db` (an empty/nonexistent file) instead of `~/.hermes/mnemosyne/data/mnemosyne.db`. The MCP server process reads that env var, so all its data landed in / read from the wrong DB while the bridge used the correct path. If MCP recall is empty but Python SDK works, check this env var first.
- Table roles inside a bank DB: `working_memory` = the live table beam queries (has `consolidated_at`, `scope`, `recall_count`...); `memories` = a legacy/compat copy (schema: id/content/source/timestamp/session_id/importance/metadata_json). The `remember()` API writes to `working_memory`; a plain DELETE on `memories` does NOT remove a memory from recall.
- **NEVER delete from FTS shadow tables manually.** `fts_working`, `fts_working_data`, `fts_working_idx`, `fts_working_content` are FTS5 shadow tables. Removing rows by hand (or cleaning "orphans") corrupts the vtable — `vtable constructor failed: fts_working` on EVERY subsequent query, including DROP. Use the `forget()` API instead.

## Python SDK API (exact signatures, v3.0.0)

```python
from mnemosyne import remember, recall, forget, get_stats
remember(content: str, source='conversation', importance=0.5, metadata=None,
         scope='session', valid_until=None, extract_entities=False, extract=False,
         bank=None, trust_tier=None) -> str(id)
recall(query: str, top_k=5, *, from_date=None, to_date=None, source=None, topic=None,
       temporal_weight=0.0, query_time=None, temporal_halflife=None,
       vec_weight=None, fts_weight=None, importance_weight=None, bank=None) -> list[dict]
forget(memory_id: str, bank=None) -> bool
```

- **First param is `content`, NOT `fact`** — `remember(fact=...)` raises `TypeError: unexpected keyword argument`. The bridge script historically called it wrong; check signatures via `inspect.signature` before assuming.
- **`bank=` is honored** by the top-level functions via `_get_default(bank)` (per-bank singleton). Earlier "bank ignored" confusion was a misread: data WAS landing in the bank, the recall call just hadn't passed `bank=`.
- Delete a test/stray memory PROPERLY: `recall('needle', bank=b)`, then `forget(hit['id'], bank=b)`. This cleans `working_memory` AND FTS. Direct `DELETE FROM working_memory` works too but leaves FTS stale — always rebuild or use forget().
- Full schema recreation: `os.remove(db)` then any call (e.g. `recall("__init__", top_k=1, bank=b)`) recreates ALL tables incl. FTS + triggers. Restore data from a dump first (backup: `shutil.copy(db, db + ".corrupt.bak")`, dump non-FTS tables via `SELECT name FROM sqlite_master WHERE type='table'` skipping `fts_*`/`vec_*`/`_vec*`, then reinsert).

## Bridge script (`~/.hermes/mnemosyne_bridge.py`)

CLI: `python3 ~/.hermes/mnemosyne_bridge.py [recall|remember|forget] ...` (venv python: `~/.venvs/mnemosyne/bin/python3`).

- `migrate_legacy()`: one-time import of `~/.hermes/memories/MEMORY.md` + `USER.md` (split on `§`) into banks `working_memory`/`user_context`; marker file `~/.hermes/mnemosyne/data/.migrated` skips re-run. Delete the marker to re-import.
- `load_memory(query)`: multi-bank recall across `working_memory`, `user_context`, `memory` — the FIXED version (2026-09) that makes bridge recall actually return data.
- `save_memory(fact, source='working_memory', importance=0.5)`: stores with `scope='global', bank='working_memory'`.

## MCP tools — fixed 2026-09

Pre-2026-09, MCP `mnemosyne_recall` returned 0 because `_resolve_bank` defaulted to bank `default` AND `MNEMOSYNE_DB_PATH` in `config.yaml` pointed at the wrong DB. Both fixed; the patches live in `site-packages` so a `pip install -U mnemosyne` wipes them. Re-apply with **`scripts/mnemosyne-mcp-repatch.sh`** (idempotent). Full diagnosis + checklist + restart sequence: **`references/mcp-recall-empty-fix.md`**. Restart the MCP process afterward (`pkill -f 'mnemosyne mcp'`; watchdog respawns) and verify via the MCP tool itself, not the SDK.

## Two separate memory layers — don't confuse them

Hermes has TWO memory stores that look similar but are independent:

| | `memory` tool (`target=user` / `target=memory`) | Mnemosyne MCP / SDK |
|---|---|---|
| On-disk location | `~/.hermes/memories/USER.md` / `MEMORY.md` | `~/.hermes/mnemosyne/data/banks/<bank>/mnemosyne.db` |
| Format | Plain markdown, entries separated by `§` | SQLite + FTS5, per-bank DBs |
| Injected into prompt | Every turn, top of context | Only on `recall` call |
| Edit via | `memory` tool (`add`/`replace`/`remove`) | `remember()`/`forget()` API or MCP tools |

The `migrate_legacy()` in the bridge one-time-imports the `.md` files INTO Mnemosyne banks, but the two stores stay in sync only at that point. After migration, edits to `USER.md` via the `memory` tool do NOT propagate to Mnemosyne, and vice versa. When the user asks "where did you save my profile?", the answer is `~/.hermes/memories/USER.md` (the `memory` tool store), NOT the Mnemosyne DB — unless you specifically used `remember()`.

## Pitfalls

- **`memory` tool `replace` fails with `No entry matched`** when the `old_text` substring doesn't byte-match the stored entry. The stored text may have been reformatted (smart quotes, trailing spaces) since you first wrote it. Read the actual `USER.md`/`MEMORY.md` to get the exact string, then retry. The tool returns `current_entries` on failure — use it.
- `memory` tool `replace` also requires `content` (the new text) AND `old_text`. Passing only `new_string` (a sed-style alias) raises `content is required for 'replace' action`.

- `sqlite3.DatabaseError: vtable constructor failed: fts_working` = FTS shadow tables corrupted (manual deletes). Don't fight it: backup-dump → `os.remove(db)` → schema-recreate → restore.
- `get_stats` reports `mode: beam`, banks listed incl. `user_context`, but `total_memories: 0` = data is in per-bank files; check `data/banks/*/mnemosyne.db` counts.
- Raw SQL INSERT into `memories` bypasses triggers — FTS never sees it → recall can't find it. Insert via `remember()` or also populate `fts_working` + `working_memory`.
- Do NOT "verify" by grepping `memories` count alone — recall queries `working_memory` + FTS.
- Recurring test rows (e.g. "chunk uji bank wm"): they pollute recall results; clean with forget() (above), not DELETE.
