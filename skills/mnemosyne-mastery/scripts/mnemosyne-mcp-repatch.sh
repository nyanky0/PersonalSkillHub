#!/usr/bin/env bash
# Re-apply Mnemosyne MCP patches after `pip install -U mnemosyne` (patches live
# in site-packages and are wiped by upgrades). Idempotent — safe to run any time.
set -euo pipefail

MCP_TOOLS="$HOME/.venvs/mnemosyne/lib/python3.14/site-packages/mnemosyne/mcp_tools.py"
CONFIG="$HOME/.hermes/config.yaml"

echo "==> [1/3] config.yaml DB path"
if grep -q "MNEMOSYNE_DB_PATH: ~/.hermes/data/mnemosyne.db" "$CONFIG"; then
  sed -i 's|MNEMOSYNE_DB_PATH: ~/.hermes/data/mnemosyne.db|MNEMOSYNE_DB_PATH: ~/.hermes/mnemosyne/data/mnemosyne.db|' "$CONFIG"
  echo "    fixed -> ~/.hermes/mnemosyne/data/mnemosyne.db"
else
  echo "    already correct, skip"
fi

echo "==> [2/3] _resolve_bank default"
if grep -q 'or "default"' "$MCP_TOOLS"; then
  sed -i 's/or "default"/or "working_memory"/' "$MCP_TOOLS"
  echo "    fixed -> working_memory"
else
  echo "    already patched, skip"
fi

echo "==> [3/3] _handle_recall multi-bank"
if grep -q '"working_memory", "user_context", "memory"' "$MCP_TOOLS"; then
  echo "    already patched, skip"
else
  python3 - <<'PY'
import pathlib
p = pathlib.Path.home() / ".venvs/mnemosyne/lib/python3.14/site-packages/mnemosyne/mcp_tools.py"
src = p.read_text()
if '"working_memory", "user_context", "memory"' in src:
    print("    already patched, skip")
else:
    old = '''    mem = _create_instance(author_id=arguments.get("author_id"), author_type=arguments.get("author_type"), channel_id=arguments.get("channel_id"), bank=bank)
    results = mem.recall(
        query=query,
        top_k=top_k,
        temporal_weight=temporal_weight,
        query_time=query_time,
        vec_weight=vec_weight,
        fts_weight=fts_weight,
        importance_weight=importance_weight,
    )

    # Serialize for JSON — datetime objects aren't JSON serializable
    serializable = []
    for r in results:
        item = dict(r) if hasattr(r, "keys") else r
        # Convert any datetime to ISO string
        for key in ["timestamp", "created_at", "valid_until", "last_recalled"]:
            if key in item and item[key] is not None:
                if hasattr(item[key], "isoformat"):
                    item[key] = item[key].isoformat()
        serializable.append(item)

    return {
        "status": "ok",
        "count": len(serializable),
        "results": serializable,
        "bank": bank
    }'''
    new = '''    # If no explicit bank given, search across all active banks and dedup.
    explicit_bank = arguments.get("bank") or os.environ.get("MNEMOSYNE_MCP_BANK")
    banks = [bank] if explicit_bank else ["working_memory", "user_context", "memory"]

    serializable = []
    seen = set()
    for b in banks:
        mem = _create_instance(author_id=arguments.get("author_id"), author_type=arguments.get("author_type"), channel_id=arguments.get("channel_id"), bank=b)
        results = mem.recall(
            query=query,
            top_k=top_k,
            temporal_weight=temporal_weight,
            query_time=query_time,
            vec_weight=vec_weight,
            fts_weight=fts_weight,
            importance_weight=importance_weight,
        )
        for r in results:
            item = dict(r) if hasattr(r, "keys") else r
            content = item.get("content", "")
            key = content[:80]
            if key in seen:
                continue
            seen.add(key)
            item["bank"] = b
            # Convert any datetime to ISO string
            for k in ["timestamp", "created_at", "valid_until", "last_recalled"]:
                if k in item and item[k] is not None:
                    if hasattr(item[k], "isoformat"):
                        item[k] = item[k].isoformat()
            serializable.append(item)

    return {
        "status": "ok",
        "count": len(serializable),
        "results": serializable,
        "bank": bank if explicit_bank else "multi"
    }'''
    if old not in src:
        raise SystemExit("    FAIL: single-bank recall block not found — check mcp_tools.py manually")
    p.write_text(src.replace(old, new))
    print("    patched")
PY
fi

echo "==> done. Restart MCP: kill mnemosyne mcp processes (watchdog respawns)."
echo "    pkill -f 'mnemosyne mcp'  # Hermes watchdog auto-respawns with new config"
