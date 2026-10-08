# 2026-09 MCP recall-empty fix (mnemosyne_recall → 0)

Symptom: Python SDK recall returns data, but MCP `mnemosyne_recall` returns
`{"status":"ok","count":0,"bank":"default"}` and `mnemosyne_get_stats` reports
0 memories while the per-bank DBs are full.

## Root cause (two independent bugs, both fixed)

1. **`MNEMOSYNE_DB_PATH` in `~/.hermes/config.yaml` pointed at the wrong file.**
   It was `~/.hermes/data/mnemosyne.db` (an empty / nonexistent DB created by the
   MCP server env). Real data lives at `~/.hermes/mnemosyne/data/banks/<bank>/mnemosyne.db`.
   The MCP server reads this env var, so it read/wrote the empty DB while the
   bridge script used the correct path. Fix:
   `sed -i 's|MNEMOSYNE_DB_PATH: ~/.hermes/data/mnemosyne.db|MNEMOSYNE_DB_PATH: ~/.hermes/mnemosyne/data/mnemosyne.db|' ~/.hermes/config.yaml`

2. **`mcp_tools.py` defaults to bank `default`.** `_resolve_bank()` fell back to
   `"default"` (the empty top-level DB) when no `bank` arg was passed; `_handle_recall`
   queried a single bank only. Patches:
   - `_resolve_bank`: `or "default"` → `or "working_memory"`
   - `_handle_recall`: when no explicit bank, loop `["working_memory", "user_context", "memory"]`,
     dedup by content[:80], tag each result with its `bank`, return `"bank": "multi"`.

   Both edits are in `~/.venvs/mnemosyne/lib/python3.14/site-packages/mnemosyne/mcp_tools.py`.
   Re-apply after any `pip install -U mnemosyne` with
   `scripts/mnemosyne-mcp-repatch.sh` (idempotent; also fixes config.yaml).

## Restart MCP after patching

The Hermes MCP client spawns one `mnemosyne mcp` process per session via a
stdio watchdog. Kill them all — the watchdog respawns fresh with new config:

```bash
pkill -f 'mnemosyne mcp'
sleep 1
pgrep -af 'mnemosyne mcp'   # should show fresh PIDs
```

Then verify through the MCP tool directly (not the Python SDK — the whole point
is that MCP now sees the data):

```
mnemosyne_recall(query="maulana configtoolkit", top_k=5)
# expect: "count": N, results tagged with "bank": "working_memory"|"user_context"|"memory"
```

## Verification checklist

- `grep MNEMOSYNE_DB_PATH ~/.hermes/config.yaml` → `~/.hermes/mnemosyne/data/mnemosyne.db`
- `grep 'or "working_memory"' .../mcp_tools.py` → present (default bank fixed)
- `grep '"working_memory", "user_context", "memory"' .../mcp_tools.py` → present (multi-bank loop)
- MCP recall returns tagged, non-zero results.

## Related gotcha from same session

FTS shadow tables (`fts_working*`) corrupted by manual DELETE leave the vtable
unusable (`vtable constructor failed: fts_working`) — even DROP fails. The
reliable repair is backup-dump → `os.remove(db)` → let the library recreate the
schema (`recall("__init__", top_k=1, bank=b)`) → restore the dump. Never hand-edit
FTS shadow tables.
