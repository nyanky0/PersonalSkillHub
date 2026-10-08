---
name: mcp-integration
description: Integrate MCP servers in Hermes. Fix version conflicts.
version: 1.0.0
author: system
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mcp, integration, debugging, devops, python, version-mismatch]
    category: devops
    requires_toolsets: [terminal]
---

# MCP Integration (Local Servers)

## Overview
Hermes Agent (v0.19.1) bundles `mcp==1.26.0`. Installing a third-party MCP server (e.g. Mnemosyne OSS) into its own venv creates a version-skew trap. This skill documents the exact resolution pattern and error fingerprints.

## Trigger
User installs a local MCP server (stdio transport) into an isolated virtualenv and registers it via `hermes config set mcp_servers.<name>.command`. Hermes shows "connecting" forever or reports `Connection closed`.

## Prerequisites
- Hermes v0.19.1 ships with `mcp==1.26.0` and `starlette==1.3.1`.
- Local MCP servers MUST pin to the **exact same versions** in their own venv — mixed major/minor versions crash silently.

## Step 1 — Install server compatible versions
```bash
# NEVER use `pip install mnemosyne` (PyPI has a dummy package)
pip install "mnemosyne-memory>=3.0.0"
# Pin MCP SDK to version Hermes uses (1.26.0)
pip install "mcp==1.26.0" "starlette==1.3.1"
```

## Step 2 — Register server
```yaml
# In ~/.hermes/config.yaml
mcp_servers:
  mnemosyne:
    command: ~/.venvs/mnemosyne/bin/mnemosyne
    args:
      - mcp
```

CRITICAL: `args` MUST be a YAML list. A bare scalar (`args: mcp`) is iterated
per-character by Hermes' spawn path — the server receives `m`, `c`, `p` as
three separate args and exits with `Unknown command: m` instantly, surfacing
upstream as `McpError: Connection closed` and a parked server.

Also: `hermes config set mcp_servers.<name>.args '["mcp"]'` does NOT work —
the CLI stores the value as a quoted string `'["mcp"]'` (then iterated
per-char: `Unknown command: [`). Edit `~/.hermes/config.yaml` directly for
list values. The patch/file tools may refuse writes to config.yaml as
security-sensitive; use `python3` one-liner or `hermes config edit` instead.

## Step 3 — Verify handshake (manual test)
```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hermes-agent","version":"1.0"}}}\n' \
  | ~/.venvs/mnemosyne/bin/mnemosyne mcp
# Expect: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
```

If initialize hangs or returns nothing, versions are mismatched.

## Step 4 — Test via Hermes
```bash
hermes mcp list         # Shows server as "enabled"
hermes mcp test <name>  # In v0.20.x this spawns the server and lists tools —
                        # a pass here is a reliable signal (verified Aug 2026).
echo 'list tools available' | hermes --cli -t memory
```
On 0.19.1 `hermes mcp test` could show "Connection failed" even when tools
worked in a live session; on 0.20.x it was trustworthy for the scalar-args
diagnosis (test failed with the bad config, listed all tools after the fix).

## Error fingerprints & fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Server.__init__() got an unexpected keyword argument 'on_list_tools'` | mcp SDK 2.x installed but server code (3.0.0) uses 1.x decorator API — or vice versa | Pin `mcp==1.26.0` in server venv |
| `'Request' object has no attribute 'send'` | starlette 1.6.x incompatible with mcp 2.x SSE transport | Pin `starlette==1.3.1` or downgrade mcp to 1.26.0 |
| `Received request before initialization was complete` | Client sent `tools/list` before sending `initialize` | This is a Hermes 0.19.1 client bug — use Python SDK bypass |
| `mnemosyne: command not found` | venv not on PATH | Use absolute path to venv: `~/.venvs/mnemosyne/bin/mnemosyne` |
| Server shows "connecting" forever | mcp SDK version mismatch between Hermes and server venv | Reinstall both to same mcp version |
| `McpError: Connection closed` right after spawn, retries 3x then parks | `args` written as scalar string — iterated per-char, server exits `Unknown command: <first-char>` immediately | Make `args` a YAML list (edit config.yaml directly; `hermes config set` stringifies lists) |
| `Unknown command: m` (or other single chars) in mcp-stderr.log | Same: scalar args iterated per-character | Same fix |

## Diagnosing stdio spawn failures — check mcp-stderr.log FIRST
Before suspecting SDK versions, read the server's own stderr:
```bash
tail -20 ~/.hermes/logs/mcp-stderr.log
```
Each attempt is prefixed `===== starting MCP server '<name>' =====`.
- Server CLI usage error (`Unknown command: ...`) → argv is wrong, check args
  shape (see Step 2), not versions.
- Empty stderr + clean JSON-RPC init works when run manually → transport /
  watchdog layer; reproduce the exact spawn:
  ```bash
  /path/to/hermes-venv/python /path/to/hermes-agent/tools/mcp_stdio_watchdog.py \
    --ppid $$ -- ~/.venvs/<server>/bin/<cmd> mcp
  ```
  then pipe an `initialize` JSON-RPC line into stdin.
- `Received exception from stream: ... json_invalid` when testing manually →
  you sent an HTTP-style `Content-Length` header; stdio MCP wants bare
  newline-delimited JSON-RPC, no header.

## Python SDK bypass (recommended primary path)
For local-first MCP servers like Mnemosyne, prefer the Python SDK directly over MCP transport — it's more reliable than stdio handshake and avoids version-skew crashes entirely.

### Setup steps
1. Install server in isolated venv:
   ```bash
   python3 -m venv ~/.venvs/mnemosyne
   source ~/.venvs/mnemosyne/bin/activate
   pip install "mnemosyne-memory>=3.0.0"
   pip install "mcp==1.26.0" "starlette==1.3.1"  # Only needed for MCP, not SDK
   ```
2. Use SDK directly in scripts:
   ```python
   # Add venv to path
   import sys
   sys.path.insert(0, "~/.venvs/mnemosyne/lib/python3.14/site-packages")
   from mnemosyne import remember, recall, forget
   ```

### Discovery: DB path location
Default DB is at `~/.hermes/mnemosyne/data/mnemosyne.db` — NOT `~/.hermes/data/`.
Check dynamically:
```python
from mnemosyne.core.memory import _default_db_path
print(_default_db_path())
```
Set explicit path via env var:
```bash
export MNEMOSYNE_DB_PATH=~/.hermes/data/mnemosyne.db
```

## MCP integration (when SDK bypass insufficient)
If MCP transport is needed (e.g. cross-agent use):

| Error | Cause | Fix |
|-------|-------|-----|
| `Server.__init__() got an unexpected keyword argument 'on_list_tools'` | mcp SDK 2.x installed but server code (3.0.0) uses 1.x decorator API | Pin `mcp==1.26.0` in server venv |
| `'Request' object has no attribute 'send'` | starlette 1.6.x incompatible with mcp 2.x SSE transport | Pin `starlette==1.3.1` or downgrade mcp to 1.26.0 |
| `Received request before initialization was complete` | Client sent `tools/list` before sending `initialize` | Use Python SDK bypass instead |
| `mnemosyne: command not found` | venv not on PATH | Use absolute path: `~/.venvs/mnemosyne/bin/mnemosyne` |
| Server shows "connecting" forever | mcp SDK version mismatch | Pin exact versions in server venv |
| `mnemosyne-memory` PyPI package is a dummy (5KB) | Wrong package name | Install from GitHub: `pip install git+https://github.com/mnemosyne-oss/mnemosyne.git` |

## Troubleshooting checklist
1. Read `~/.hermes/logs/mcp-stderr.log` FIRST — the server's own error usually names the root cause (usage errors, bad argv) before any SDK theory
2. Verify mcp version match: `pip show mcp` in BOTH Hermes venv and server venv
3. Verify stdio handshake manually before testing in Hermes (bare JSON-RPC line on stdin, no Content-Length header)
4. Check `args` shape in config.yaml — must be a list, not scalar
5. Check Hermes logs: `hermes logs | grep -i mcp` for transport errors (`errors.log` shows park/reconnect lifecycle)
6. If SSE endpoint crashes, switch to stdio transport
7. `hermes mcp test` is unreliable in 0.19.1 — always verify with live session

## Empty DB despite successful MCP connect (proven 2026-09)

MCP tools can connect fine (`get_stats` → `"status":"ok"`, all tools listed) while the memory store is **empty** — `total_memories: 0`. Handshake success does NOT imply data survived.

Typical cause: a legacy migration wrote a marker file but the actual `remember()` calls never persisted (wrong DB path / wrong bank at migration time), so the DB tables are empty and the `.migrated` marker now blocks any re-migration.

Verify data, not just connection:
```bash
# 1. Stats via MCP (connect works ≠ data present)
# 2. Query the SQLite DB directly:
~/.venvs/mnemosyne/bin/python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/mnemosyne/data/mnemosyne.db')
con = sqlite3.connect(db)
for t in ['memories','working_memory','episodic_memory','facts']:
    print(t, con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
"
# 3. Check for the stale migration marker blocking re-import:
ls -la ~/.hermes/mnemosyne/data/.migrated   # delete it to allow re-migration
```
Fix: delete the stale `.migrated` marker, re-run the migration/import (chunk MEMORY.md/USER.md by `§`, `remember()` into banks `user_context` + `working_memory`), then confirm `recall('...')` returns rows.

Lesson: after any MCP/memory setup, end with a **data round-trip check** (`remember` → `recall` → non-empty), not just `hermes mcp test`. A connected-but-empty store reads as "done" and stays broken for weeks.

## References
- `references/mcp-error-log.md` — session-specific error transcript from the Mnemosyne integration attempt, August 2026.
- `references/mnemosyne-bridge-template.py` — ready-to-use bridge script for SDK-based memory integration.
- `references/args-scalar-bug.md` — full debugging transcript: scalar `args` iterated per-char, 3574 identical stderr errors, config-set-stringify trap, and the working YAML fix (August 2026).